from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from app.shared.enums import Gender


class TeacherBase(BaseModel):
    """Base teacher schema"""
    school_id: int
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    gender: Gender
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    employee_id: str = Field(..., min_length=1, max_length=50)
    joining_date: date
    designation: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    qualification: Optional[str] = Field(None, max_length=200)
    specialization: Optional[str] = Field(None, max_length=200)


class TeacherCreate(TeacherBase):
    """Schema for creating a teacher"""
    pass


class TeacherUpdate(BaseModel):
    """Schema for updating a teacher"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    designation: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    qualification: Optional[str] = Field(None, max_length=200)
    specialization: Optional[str] = Field(None, max_length=200)


class Teacher(TeacherBase):
    """Schema for teacher response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
