from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.tenancy.database import get_master_db
from app.tenancy.models import SuperAdmin
from app.core.security import verify_password, create_access_token
from app.modules.super_admin.schemas import SuperAdminLoginRequest, Token

router = APIRouter(prefix="/generated-admin", tags=["Super Admin"])

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
        select(SuperAdmin).where(SuperAdmin.username == login_data.username)
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
