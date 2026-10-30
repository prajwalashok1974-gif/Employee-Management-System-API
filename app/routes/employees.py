from app.routes.auth import get_current_user, require_admin
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeePartialUpdate,
    EmployeeResponse
)



router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
    dependencies=[Depends(get_current_user)]
)


# CREATE EMPLOYEE
@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db)
):

    existing_employee = db.query(Employee).filter(
        Employee.email == str(employee_data.email)
    ).first()

    if existing_employee:
        raise HTTPException(
            status_code=409,
            detail="Employee with this email already exists"
        )

    new_employee = Employee(
        **employee_data.model_dump()
    )

    try:
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Employee with this email already exists"
        )

    return new_employee


# GET ALL EMPLOYEES WITH SEARCH, FILTER AND PAGINATION
@router.get("/", response_model=list[EmployeeResponse])
def get_all_employees(
    search: Optional[str] = None,
    department: Optional[str] = None,
    employee_status: Optional[str] = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):

    query = db.query(Employee)

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Employee.name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.role.ilike(search_term)
            )
        )

    if department:
        query = query.filter(
            Employee.department.ilike(department)
        )

    if employee_status:
        query = query.filter(
            Employee.status.ilike(employee_status)
        )

    employees = (
        query.order_by(Employee.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return employees


# GET EMPLOYEE BY ID
@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee


# UPDATE COMPLETE EMPLOYEE
@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    duplicate_email = db.query(Employee).filter(
        Employee.email == str(employee_data.email),
        Employee.id != employee_id
    ).first()

    if duplicate_email:
        raise HTTPException(
            status_code=409,
            detail="Email already belongs to another employee"
        )

    for key, value in employee_data.model_dump().items():
        setattr(employee, key, value)

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return employee


# PARTIAL UPDATE EMPLOYEE
@router.patch("/{employee_id}", response_model=EmployeeResponse)
def partial_update_employee(
    employee_id: int,
    employee_data: EmployeePartialUpdate,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    update_data = employee_data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:

        duplicate_email = db.query(Employee).filter(
            Employee.email == str(update_data["email"]),
            Employee.id != employee_id
        ).first()

        if duplicate_email:
            raise HTTPException(
                status_code=409,
                detail="Email already belongs to another employee"
            )

        update_data["email"] = str(update_data["email"])

    for key, value in update_data.items():
        setattr(employee, key, value)

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Unable to update employee because of a database conflict"
        )

    return employee


# DELETE EMPLOYEE
@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    db.delete(employee)
    db.commit()

    return {
        "message": "Employee deleted successfully",
        "employee_id": employee_id
    }


# EMPLOYEE STATISTICS
@router.get("/stats/summary")
def employee_statistics(
    db: Session = Depends(get_db)
):

    total_employees = db.query(Employee).count()

    active_employees = db.query(Employee).filter(
        Employee.status == "Active"
    ).count()

    inactive_employees = db.query(Employee).filter(
        Employee.status == "Inactive"
    ).count()

    on_leave_employees = db.query(Employee).filter(
        Employee.status == "On Leave"
    ).count()

    average_salary = db.query(
        func.avg(Employee.salary)
    ).scalar()

    total_salary = db.query(
        func.sum(Employee.salary)
    ).scalar()

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
        "on_leave_employees": on_leave_employees,
        "average_salary": round(float(average_salary or 0), 2),
        "total_monthly_salary": int(total_salary or 0)
    }