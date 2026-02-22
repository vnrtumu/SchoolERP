from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.tenancy.database import get_tenant_db
from app.modules.branches.models import Branch
from app.rbac.decorators import require_role, branch_scoped
from app.rbac.constants import Role
from pydantic import BaseModel
from typing import Optional


router = APIRouter()


# ── Response Schemas ──

class BranchStatsResponse(BaseModel):
    """Dashboard statistics for a specific branch."""
    branch_id: int
    branch_name: str
    branch_code: str
    is_main_branch: bool
    # Counts (placeholder — will be populated when models are linked)
    student_count: int = 0
    teacher_count: int = 0
    course_count: int = 0
    total_fees_collected: float = 0.0
    pending_fees: float = 0.0


class BranchProfileResponse(BaseModel):
    """Full branch profile for the branch admin."""
    id: int
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_main_branch: bool
    is_active: bool


# ── Endpoints ──

@router.get("/stats", response_model=BranchStatsResponse)
@require_role(Role.BRANCH_ADMIN, Role.BRANCH_PRINCIPAL)
@branch_scoped
async def get_branch_stats(
    db: AsyncSession = Depends(get_tenant_db),
    current_user=None,
    branch_id: int = None,
):
    """
    Get dashboard statistics for the current user's branch.
    
    Branch ID is auto-injected by @branch_scoped decorator.
    """
    if not branch_id:
        raise HTTPException(
            status_code=400,
            detail="Branch context not available"
        )
    
    # Get branch info
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=404,
            detail=f"Branch {branch_id} not found"
        )
    
    # TODO: When Student, Teacher, Course models have branch_id,
    # query actual counts here. For now, return zeros.
    # Example:
    # student_count = await db.scalar(
    #     select(func.count()).select_from(Student).where(Student.branch_id == branch_id)
    # )
    
    return BranchStatsResponse(
        branch_id=branch.id,
        branch_name=branch.name,
        branch_code=branch.code,
        is_main_branch=branch.is_main_branch,
        student_count=0,
        teacher_count=0,
        course_count=0,
        total_fees_collected=0.0,
        pending_fees=0.0,
    )


@router.get("/profile", response_model=BranchProfileResponse)
@require_role(Role.BRANCH_ADMIN, Role.BRANCH_PRINCIPAL)
@branch_scoped
async def get_branch_profile(
    db: AsyncSession = Depends(get_tenant_db),
    current_user=None,
    branch_id: int = None,
):
    """
    Get the full profile of the current user's branch.
    """
    if not branch_id:
        raise HTTPException(
            status_code=400,
            detail="Branch context not available"
        )
    
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=404,
            detail=f"Branch {branch_id} not found"
        )
    
    return BranchProfileResponse(
        id=branch.id,
        name=branch.name,
        code=branch.code,
        address=branch.address,
        phone=branch.phone,
        email=branch.email,
        is_main_branch=branch.is_main_branch,
        is_active=branch.is_active,
    )
