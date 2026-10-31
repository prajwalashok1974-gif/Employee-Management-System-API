from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="employee")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    employee_id = Column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False, default="Unassigned")
    salary = Column(Integer, nullable=False)
    employment_type = Column(String(50), nullable=False, default="Full-time")
    status = Column(String(30), nullable=False, default="Active")
    hire_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
