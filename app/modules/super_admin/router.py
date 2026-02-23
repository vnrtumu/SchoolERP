from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.tenancy.database import get_master_db
from app.tenancy.models import SuperAdmin
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_current_super_admin
from app.modules.super_admin.schemas import SuperAdminLoginRequest, Token, SuperAdminResponse, SuperAdminUpdateRequest

router = APIRouter(tags=["Super Admin"])

@router.post("/login", response_model=Token)
async def login(
    login_data: SuperAdminLoginRequest,
    db: AsyncSession = Depends(get_master_db)
):
    """
    Super Admin Login
    
    Authenticates a super admin against the master database.
    """
    # Query user from master DB
    result = await db.execute(
        select(SuperAdmin).where(
            or_(
                SuperAdmin.username == login_data.username,
                SuperAdmin.email == login_data.username
            )
        )
    )
    user = result.scalar_one_or_none()
    
    # Verify user exists and password matches
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": "super_admin",
            "type": "super_admin"
        }
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=SuperAdminResponse)
async def get_current_user(
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Get current logged in Super Admin details.
    """
    result = await db.execute(
        select(SuperAdmin).where(SuperAdmin.id == int(current_admin["sub"]))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Super Admin not found"
        )
        
    return SuperAdminResponse.model_validate(user)

@router.put("/me", response_model=SuperAdminResponse)
async def update_current_user(
    update_data: SuperAdminUpdateRequest,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Update current logged in Super Admin details.
    """
    result = await db.execute(
        select(SuperAdmin).where(SuperAdmin.id == int(current_admin["sub"]))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Super Admin not found"
        )
        
    # Update fields provided in request
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)
        
    await db.commit()
    await db.refresh(user)
    
    return SuperAdminResponse.model_validate(user)
