from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.modules.courses import schemas, models
from app.core.dependencies import Pagination
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=list[schemas.Course])
def list_courses(
    school_id: Optional[int] = None,
    grade: Optional[str] = None,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db)
):
    """List all courses"""
    query = db.query(models.Course)
    if school_id:
        query = query.filter(models.Course.school_id == school_id)
    if grade:
        query = query.filter(models.Course.grade == grade)
    courses = query.offset(pagination.skip).limit(pagination.limit).all()
    return courses


@router.get("/{course_id}", response_model=schemas.Course)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get course by ID"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise NotFoundException(f"Course with ID {course_id} not found")
    return course


@router.post("/", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
def create_course(course_data: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Create a new course"""
    course = models.Course(**course_data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.patch("/{course_id}", response_model=schemas.Course)
def update_course(
    course_id: int,
    course_data: schemas.CourseUpdate,
    db: Session = Depends(get_db)
):
    """Update a course"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise NotFoundException(f"Course with ID {course_id} not found")
    
    update_data = course_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise NotFoundException(f"Course with ID {course_id} not found")
    
    db.delete(course)
    db.commit()
    return None
