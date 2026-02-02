from sqlalchemy.orm import Session
from typing import Optional
from app.modules.auth import models, schemas
from app.core.exceptions import NotFoundException, ConflictException
from app.core.security import get_password_hash


class UserRepository:
    """Data access layer for users"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[models.User]:
        """Get user by ID"""
        return self.db.query(models.User).filter(models.User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[models.User]:
        """Get user by email"""
        return self.db.query(models.User).filter(models.User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[models.User]:
        """Get user by username"""
        return self.db.query(models.User).filter(models.User.username == username).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, school_id: Optional[int] = None) -> list[models.User]:
        """Get all users with pagination and optional school filter"""
        query = self.db.query(models.User)
        if school_id:
            query = query.filter(models.User.school_id == school_id)
        return query.offset(skip).limit(limit).all()
    
    def create(self, user_data: schemas.UserCreate) -> models.User:
        """Create a new user"""
        # Check if email or username already exists
        if self.get_by_email(user_data.email):
            raise ConflictException(f"User with email '{user_data.email}' already exists")
        if self.get_by_username(user_data.username):
            raise ConflictException(f"User with username '{user_data.username}' already exists")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        user_dict = user_data.model_dump(exclude={"password"})
        user = models.User(**user_dict, hashed_password=hashed_password)
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user_id: int, user_data: schemas.UserUpdate) -> models.User:
        """Update a user"""
        user = self.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Check email uniqueness if being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing = self.get_by_email(update_data["email"])
            if existing:
                raise ConflictException(f"User with email '{update_data['email']}' already exists")
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete a user (soft delete)"""
        user = self.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        user.is_active = False
        self.db.commit()
        return True
