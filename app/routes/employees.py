from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, User
from app.routes.auth import get_current_user, require_admin_or_hr
from app.schemas import EmployeeCreate, EmployeeUpdate, EmployeePartialUpdate, EmployeeResponse

router = APIRouter(prefix="/employees", tags=["Employees"])


class LinkAccountRequest(BaseModel):
    user_id: int = Field(gt=0)


@router.get("/me", response_model=EmployeeResponse)
def get_my_employee_record(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "employee":
        raise HTTPException(status_code=400, detail="This endpoint is intended for employee accounts")
    if current_user.employee_id is None:
        raise HTTPException(status_code=404, detail="No employee record is linked to this account")
    employee = db.query(Employee).filter(Employee.id == current_user.employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee record not found")
    return employee


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    employee = Employee(**employee_data.model_dump())
    try:
        db.add(employee)
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Employee email already exists")
    return employee


@router.get("/", response_model=list[EmployeeResponse])
def get_all_employees(
    search: Optional[str] = None,
    department: Optional[str] = None,
    employee_status: Optional[str] = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    query = db.query(Employee)
    if search:
        term = f"%{search}%"
        query = query.filter(or_(Employee.name.ilike(term), Employee.email.ilike(term), Employee.role.ilike(term)))
    if department:
        query = query.filter(Employee.department.ilike(department))
    if employee_status:
        query = query.filter(Employee.status.ilike(employee_status))
    return query.order_by(Employee.id.desc()).offset(skip).limit(limit).all()


@router.get("/stats/summary")
def employee_statistics(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    average_salary = db.query(func.avg(Employee.salary)).scalar()
    total_salary = db.query(func.sum(Employee.salary)).scalar()
    return {
        "total_employees": db.query(Employee).count(),
        "active_employees": db.query(Employee).filter(Employee.status == "Active").count(),
        "inactive_employees": db.query(Employee).filter(Employee.status == "Inactive").count(),
        "on_leave_employees": db.query(Employee).filter(Employee.status == "On Leave").count(),
        "average_salary": round(float(average_salary or 0), 2),
        "total_monthly_salary": int(total_salary or 0),
    }


@router.post("/{employee_id}/link-account", status_code=status.HTTP_200_OK)
def link_employee_account(
    employee_id: int,
    payload: LinkAccountRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User account not found")
    if user.role != "employee":
        raise HTTPException(status_code=400, detail="Only employee accounts can be linked")
    if user.employee_id not in (None, employee_id):
        raise HTTPException(status_code=409, detail="User is already linked to another employee")
    linked_user = db.query(User).filter(User.employee_id == employee_id, User.id != user.id).first()
    if linked_user:
        raise HTTPException(status_code=409, detail="Employee already has a linked account")
    user.employee_id = employee_id
    db.commit()
    return {"message": "Employee account linked successfully", "employee_id": employee_id, "user_id": user.id}


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in employee_data.model_dump().items():
        setattr(employee, key, value)
    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Employee email already exists")
    return employee


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def partial_update_employee(
    employee_id: int,
    employee_data: EmployeePartialUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in employee_data.model_dump(exclude_unset=True).items():
        setattr(employee, key, value)
    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Employee email already exists")
    return employee


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully", "employee_id": employee_id}
