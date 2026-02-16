from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.tenancy.database import get_tenant_db
from app.modules.branches.models import Branch
from app.modules.branches.schemas import (
    BranchCreate,
    BranchUpdate,
    BranchResponse,
    BranchListResponse
)
from app.rbac.decorators import require_permissions, require_role
from app.rbac.constants import Permission, Role

router = APIRouter()


@router.get("/", response_model=BranchListResponse)
@require_permissions(Permission.BRANCH_VIEW)
async def list_branches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user=None  # Injected by decorator
):
    """
    List all branches with pagination.
    
    Access control is handled by the @require_permissions decorator.
    """
    query = select(Branch)
    
    # Filter by active status if specified
    if is_active is not None:
        query = query.where(Branch.is_active == is_active)
    
    # Branch-level roles see only their branch (handled by user's primary_branch_id)
    # Note: Full branch filtering will be implemented when entities (students/teachers) are linked to branches
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    branches = result.scalars().all()
    
    return BranchListResponse(
        branches=[BranchResponse.model_validate(b) for b in branches],
        total=total
    )


@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(Permission.BRANCH_CREATE)
async def create_branch(
    branch_data: BranchCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user=None  # Injected by decorator
):
    """
    Create a new branch.
    
    Requires BRANCH_CREATE permission (typically SCHOOL_ADMIN only).
    """
    # Check if code already exists
    existing = await db.execute(
        select(Branch).where(Branch.code == branch_data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Branch with code '{branch_data.code}' already exists"
        )
    
    # Create new branch
    new_branch = Branch(**branch_data.model_dump())
    db.add(new_branch)
    await db.commit()
    await db.refresh(new_branch)
    
    return BranchResponse.model_validate(new_branch)


@router.get("/{branch_id}", response_model=BranchResponse)
@require_permissions(Permission.BRANCH_VIEW)
async def get_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user=None  # Injected by decorator
):
    """
   Get a specific branch by ID.
    """
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with ID {branch_id} not found"
        )
    
    return BranchResponse.model_validate(branch)


@router.put("/{branch_id}", response_model=BranchResponse)
@require_permissions(Permission.BRANCH_EDIT)
async def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user=None  # Injected by decorator
):
    """
    Update a branch.
    
    Requires BRANCH_EDIT permission.
    """
    # Get the branch
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with ID {branch_id} not found"
        )
    
    # Update fields
    update_data = branch_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)
    
    await db.commit()
    await db.refresh(branch)
    
    return BranchResponse.model_validate(branch)


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(Permission.BRANCH_DELETE)
async def delete_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user=None  # Injected by decorator
):
    """
    Delete (deactivate) a branch.
    
    Requires BRANCH_DELETE permission (typically SCHOOL_ADMIN only).
    Note: This deactivates the branch rather than deleting it.
    """
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with ID {branch_id} not found"
        )
    
    # Check if this is the main branch
    if branch.is_main_branch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the main branch"
        )
    
    # Deactivate instead of delete
    branch.is_active = False
    await db.commit()
    
    return None
