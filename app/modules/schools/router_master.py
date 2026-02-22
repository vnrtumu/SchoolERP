from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import secrets
from app.tenancy.database import get_master_db
from app.tenancy.models import School
from app.core.security import get_password_hash
from app.core.dependencies import get_current_super_admin
from app.tenancy.provisioning import provision_new_tenant
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


router = APIRouter()


# Schemas for master-level school (tenant) management
class SchoolCreateMaster(BaseModel):
    """Schema for creating a new school/tenant"""
    subdomain: str = Field(..., min_length=2, max_length=100, description="Unique subdomain")
    name: str = Field(..., min_length=2, max_length=200, description="School name")
    code: str = Field(..., min_length=2, max_length=50, description="Unique school code")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    
    # Database configuration
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=3306, ge=1, le=65535)
    db_user: str = Field(default="root")
    db_password: str = Field(..., description="Database password")
    
    # Subscription
    max_students: Optional[int] = Field(None, ge=0)
    max_teachers: Optional[int] = Field(None, ge=0)
    subscription_tier: Optional[str] = Field("basic", max_length=50)


class SchoolUpdateMaster(BaseModel):
    """Schema for updating a school"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    max_students: Optional[int] = Field(None, ge=0)
    max_teachers: Optional[int] = Field(None, ge=0)
    subscription_tier: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class SchoolResponseMaster(BaseModel):
    """Schema for school response (master database)"""
    id: int
    subdomain: str
    name: str
    code: str
    email: Optional[str]
    phone: Optional[str]
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    max_students: Optional[int]
    max_teachers: Optional[int]
    subscription_tier: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SchoolListResponseMaster(BaseModel):
    """Schema for list of schools"""
    schools: list[SchoolResponseMaster]
    total: int


@router.get("/", response_model=SchoolListResponseMaster)
async def list_schools(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = None,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    List all schools (tenants).
    
    Only accessible by SUPER_ADMIN.
    """
    query = select(School)
    
    # Filter by active status
    if is_active is not None:
        query = query.where(School.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(School.created_at.desc())
    result = await db.execute(query)
    schools = result.scalars().all()
    
    return SchoolListResponseMaster(
        schools=[SchoolResponseMaster.model_validate(s) for s in schools],
        total=total
    )


@router.post("/", response_model=SchoolResponseMaster, status_code=status.HTTP_201_CREATED)
async def create_school(
    school_data: SchoolCreateMaster,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Create a new school (tenant).
    
    This creates an entry in the master database registry.
    Note: The actual tenant database must be created separately and migrations run.
    
    Only accessible by SUPER_ADMIN.
    """
    # Check if subdomain already exists
    existing_subdomain = await db.execute(
        select(School).where(School.subdomain == school_data.subdomain)
    )
    if existing_subdomain.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subdomain '{school_data.subdomain}' already exists"
        )
    
    # Check if code already exists
    existing_code = await db.execute(
        select(School).where(School.code == school_data.code)
    )
    if existing_code.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"School code '{school_data.code}' already exists"
        )
    
    # Generate database name from subdomain
    db_name = f"{school_data.subdomain.lower().replace('-', '_')}_db"
    
    # Actually create the Database and apply schema structure via Alembic
    success = await provision_new_tenant(db_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to provision database '{db_name}'. Please check server logs."
        )
    
    # Encrypt database password
    encrypted_password = get_password_hash(school_data.db_password)
    
    # Create new school
    new_school = School(
        subdomain=school_data.subdomain,
        name=school_data.name,
        code=school_data.code,
        email=school_data.email,
        phone=school_data.phone,
        db_host=school_data.db_host,
        db_port=school_data.db_port,
        db_name=db_name,
        db_user=school_data.db_user,
        db_password_encrypted=encrypted_password,
        max_students=school_data.max_students,
        max_teachers=school_data.max_teachers,
        subscription_tier=school_data.subscription_tier,
        is_active=True
    )
    
    db.add(new_school)
    await db.commit()
    await db.refresh(new_school)
    
    return SchoolResponseMaster.model_validate(new_school)


@router.get("/{school_id}", response_model=SchoolResponseMaster)
async def get_school(
    school_id: int,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Get a specific school by ID.
    
    Only accessible by SUPER_ADMIN.
    """
    result = await db.execute(
        select(School).where(School.id == school_id)
    )
    school = result.scalar_one_or_none()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"School with ID {school_id} not found"
        )
    
    return SchoolResponseMaster.model_validate(school)


@router.put("/{school_id}", response_model=SchoolResponseMaster)
async def update_school(
    school_id: int,
    school_data: SchoolUpdateMaster,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Update a school's information.
    
    Only accessible by SUPER_ADMIN.
    """
    # Get the school
    result = await db.execute(
        select(School).where(School.id == school_id)
    )
    school = result.scalar_one_or_none()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"School with ID {school_id} not found"
        )
    
    # Update fields
    update_data = school_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(school, field, value)
    
    await db.commit()
    await db.refresh(school)
    
    return SchoolResponseMaster.model_validate(school)


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(
    school_id: int,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Delete (deactivate) a school.
    
    This deactivates the school rather than hard-deleting it.
    
    Only accessible by SUPER_ADMIN.
    """
    result = await db.execute(
        select(School).where(School.id == school_id)
    )
    school = result.scalar_one_or_none()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"School with ID {school_id} not found"
        )
    
    # Deactivate instead of delete
    school.is_active = False
    await db.commit()
    
    return None
