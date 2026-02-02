from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SchoolBase(BaseModel):
    """Base school/tenant schema"""
    subdomain: str = Field(..., min_length=3, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = None
    phone: Optional[str] = None
    max_students: Optional[int] = None
    max_teachers: Optional[int] = None
    subscription_tier: Optional[str] = None


class SchoolCreate(SchoolBase):
    """Schema for creating a new tenant"""
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str  # Will be encrypted before storage


class SchoolUpdate(BaseModel):
    """Schema for updating tenant details"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    max_students: Optional[int] = None
    max_teachers: Optional[int] = None
    subscription_tier: Optional[str] = None


class School(SchoolBase):
    """Schema for tenant response"""
    id: int
    is_active: bool
    db_host: str
    db_port: int
    db_name: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class TenantContext(BaseModel):
    """Tenant context for request scope"""
    tenant_id: int
    tenant_name: str
    subdomain: str
    is_active: bool
