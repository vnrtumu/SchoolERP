from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CourseBase(BaseModel):
    """Base course schema"""
    school_id: int
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    grade: str = Field(..., min_length=1, max_length=20)
    credits: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=50)


class CourseCreate(CourseBase):
    """Schema for creating a course"""
    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    credits: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=50)


class Course(CourseBase):
    """Schema for course response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
