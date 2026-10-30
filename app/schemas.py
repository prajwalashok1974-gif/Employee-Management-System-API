from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeBase(BaseModel):

    name: str = Field(min_length=2, max_length=100)

    email: EmailStr

    phone: Optional[str] = Field(default=None, max_length=20)

    role: str = Field(min_length=2, max_length=100)

    department: str = Field(default="Unassigned", max_length=100)

    salary: int = Field(ge=0)

    employment_type: str = Field(default="Full-time", max_length=50)

    status: str = Field(default="Active", max_length=30)

    hire_date: Optional[date] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeePartialUpdate(BaseModel):

    name: Optional[str] = Field(default=None, min_length=2, max_length=100)

    email: Optional[EmailStr] = None

    phone: Optional[str] = Field(default=None, max_length=20)

    role: Optional[str] = Field(default=None, min_length=2, max_length=100)

    department: Optional[str] = Field(default=None, max_length=100)

    salary: Optional[int] = Field(default=None, ge=0)

    employment_type: Optional[str] = Field(default=None, max_length=50)

    status: Optional[str] = Field(default=None, max_length=30)

    hire_date: Optional[date] = None


class EmployeeResponse(EmployeeBase):

    id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)