from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.schools import schemas
from app.modules.schools.service import SchoolService
from app.core.dependencies import Pagination

router = APIRouter(prefix="/schools", tags=["Schools"])


@router.get("/", response_model=list[schemas.School])
def list_schools(
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db)
):
    """List all schools"""
    service = SchoolService(db)
    return service.list_schools(skip=pagination.skip, limit=pagination.limit)


@router.get("/{school_id}", response_model=schemas.School)
def get_school(school_id: int, db: Session = Depends(get_db)):
    """Get school by ID"""
    service = SchoolService(db)
    return service.get_school(school_id)


@router.post("/", response_model=schemas.School, status_code=status.HTTP_201_CREATED)
def create_school(school_data: schemas.SchoolCreate, db: Session = Depends(get_db)):
    """Create a new school"""
    service = SchoolService(db)
    return service.create_school(school_data)


@router.patch("/{school_id}", response_model=schemas.School)
def update_school(
    school_id: int,
    school_data: schemas.SchoolUpdate,
    db: Session = Depends(get_db)
):
    """Update a school"""
    service = SchoolService(db)
    return service.update_school(school_id, school_data)


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_school(school_id: int, db: Session = Depends(get_db)):
    """Delete a school (soft delete)"""
    service = SchoolService(db)
    service.delete_school(school_id)
    return None
