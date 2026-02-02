from sqlalchemy.orm import Session
from app.modules.schools import schemas
from app.modules.schools.repository import SchoolRepository


class SchoolService:
    """Business logic layer for schools"""
    
    def __init__(self, db: Session):
        self.repository = SchoolRepository(db)
    
    def get_school(self, school_id: int) -> schemas.School:
        """Get school by ID"""
        school = self.repository.get_by_id(school_id)
        return schemas.School.model_validate(school)
    
    def list_schools(self, skip: int = 0, limit: int = 100) -> list[schemas.School]:
        """List all schools"""
        schools = self.repository.get_all(skip, limit)
        return [schemas.School.model_validate(school) for school in schools]
    
    def create_school(self, school_data: schemas.SchoolCreate) -> schemas.School:
        """Create a new school"""
        school = self.repository.create(school_data)
        return schemas.School.model_validate(school)
    
    def update_school(self, school_id: int, school_data: schemas.SchoolUpdate) -> schemas.School:
        """Update a school"""
        school = self.repository.update(school_id, school_data)
        return schemas.School.model_validate(school)
    
    def delete_school(self, school_id: int) -> bool:
        """Delete a school"""
        return self.repository.delete(school_id)
