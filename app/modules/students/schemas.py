from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from app.shared.enums import Gender


class StudentBase(BaseModel):
    """Base student schema"""
    school_id: int
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    gender: Gender
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    admission_number: str = Field(..., min_length=1, max_length=50)
    admission_date: date
    current_grade: str = Field(..., min_length=1, max_length=20)
    section: Optional[str] = Field(None, max_length=10)
    parent_name: Optional[str] = Field(None, max_length=100)
    parent_phone: Optional[str] = Field(None, max_length=20)
    parent_email: Optional[EmailStr] = None


class StudentCreate(StudentBase):
    """Schema for creating a student"""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating a student"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    current_grade: Optional[str] = Field(None, min_length=1, max_length=20)
    section: Optional[str] = Field(None, max_length=10)
    parent_name: Optional[str] = Field(None, max_length=100)
    parent_phone: Optional[str] = Field(None, max_length=20)
    parent_email: Optional[EmailStr] = None


class Student(StudentBase):
    """Schema for student response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
