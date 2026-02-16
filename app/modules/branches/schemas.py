from pydantic import BaseModel, Field
from typing import Optional


class BranchBase(BaseModel):
    """Base schema for Branch"""
    name: str = Field(..., min_length=1, max_length=255, description="Branch name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique branch code")
    address: Optional[str] = Field(None, description="Branch address")
    phone: Optional[str] = Field(None, max_length=20, description="Branch phone number")
    email: Optional[str] = Field(None, max_length=255, description="Branch email")
    is_main_branch: bool = Field(default=False, description="Is this the main/primary branch?")
    is_active: bool = Field(default=True, description="Is this branch active?")


class BranchCreate(BranchBase):
    """Schema for creating a new branch"""
    pass


class BranchUpdate(BaseModel):
    """Schema for updating a branch"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    is_main_branch: Optional[bool] = None
    is_active: Optional[bool] = None


class BranchResponse(BranchBase):
    """Schema for branch response"""
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BranchListResponse(BaseModel):
    """Schema for list of branches"""
    branches: list[BranchResponse]
    total: int
