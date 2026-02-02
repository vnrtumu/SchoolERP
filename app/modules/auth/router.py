from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.modules.auth import schemas
from app.modules.auth.service import AuthService
from app.core.dependencies import Pagination, get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token"""
    service = AuthService(db)
    return service.authenticate_user(login_data.username, login_data.password)


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    service = AuthService(db)
    return service.create_user(user_data)


@router.get("/me", response_model=schemas.User)
def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    service = AuthService(db)
    return service.get_user(current_user_id)


@router.get("/users", response_model=list[schemas.User])
def list_users(
    school_id: Optional[int] = None,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db)
):
    """List all users"""
    service = AuthService(db)
    return service.list_users(skip=pagination.skip, limit=pagination.limit, school_id=school_id)


@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    service = AuthService(db)
    return service.get_user(user_id)


@router.patch("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a user"""
    service = AuthService(db)
    return service.update_user(user_id, user_data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    service = AuthService(db)
    service.delete_user(user_id)
    return None
