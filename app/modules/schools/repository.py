from sqlalchemy.orm import Session
from typing import Optional
from app.modules.schools import models, schemas
from app.core.exceptions import NotFoundException, ConflictException


class SchoolRepository:
    """Data access layer for schools"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, school_id: int) -> Optional[models.School]:
        """Get school by ID"""
        return self.db.query(models.School).filter(models.School.id == school_id).first()
    
    def get_by_code(self, code: str) -> Optional[models.School]:
        """Get school by code"""
        return self.db.query(models.School).filter(models.School.code == code).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[models.School]:
        """Get all schools with pagination"""
        return self.db.query(models.School).offset(skip).limit(limit).all()
    
    def create(self, school_data: schemas.SchoolCreate) -> models.School:
        """Create a new school"""
        # Check if code already exists
        existing = self.get_by_code(school_data.code)
        if existing:
            raise ConflictException(f"School with code '{school_data.code}' already exists")
        
        school = models.School(**school_data.model_dump())
        self.db.add(school)
        self.db.commit()
        self.db.refresh(school)
        return school
    
    def update(self, school_id: int, school_data: schemas.SchoolUpdate) -> models.School:
        """Update a school"""
        school = self.get_by_id(school_id)
        if not school:
            raise NotFoundException(f"School with ID {school_id} not found")
        
        update_data = school_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(school, field, value)
        
        self.db.commit()
        self.db.refresh(school)
        return school
    
    def delete(self, school_id: int) -> bool:
        """Delete a school (soft delete by setting is_active=False)"""
        school = self.get_by_id(school_id)
        if not school:
            raise NotFoundException(f"School with ID {school_id} not found")
        
        school.is_active = False
        self.db.commit()
        return True
