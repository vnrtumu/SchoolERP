from sqlalchemy.orm import Session
from typing import Optional
from app.modules.auth import schemas
from app.modules.auth.repository import UserRepository
from app.core.security import verify_password, create_access_token
from app.core.exceptions import UnauthorizedException


class AuthService:
    """Business logic layer for authentication"""
    
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def authenticate_user(self, username: str, password: str) -> Optional[schemas.Token]:
        """Authenticate user and return access token"""
        user = self.repository.get_by_username(username)
        
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect username or password")
        
        if not user.is_active:
            raise UnauthorizedException("User account is inactive")
        
        # Create access token with user info
        access_token = create_access_token(
            data={
                "sub": user.id,
                "username": user.username,
                "role": user.role.value,
                "school_id": user.school_id
            }
        )
        
        return schemas.Token(access_token=access_token)
    
    def get_user(self, user_id: int) -> schemas.User:
        """Get user by ID"""
        user = self.repository.get_by_id(user_id)
        return schemas.User.model_validate(user)
    
    def list_users(self, skip: int = 0, limit: int = 100, school_id: Optional[int] = None) -> list[schemas.User]:
        """List all users"""
        users = self.repository.get_all(skip, limit, school_id)
        return [schemas.User.model_validate(user) for user in users]
    
    def create_user(self, user_data: schemas.UserCreate) -> schemas.User:
        """Create a new user"""
        user = self.repository.create(user_data)
        return schemas.User.model_validate(user)
    
    def update_user(self, user_id: int, user_data: schemas.UserUpdate) -> schemas.User:
        """Update a user"""
        user = self.repository.update(user_id, user_data)
        return schemas.User.model_validate(user)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        return self.repository.delete(user_id)
