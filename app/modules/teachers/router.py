from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.modules.teachers import schemas, models
from app.core.dependencies import Pagination
from app.core.exceptions import NotFoundException, ConflictException

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/", response_model=list[schemas.Teacher])
def list_teachers(
    school_id: Optional[int] = None,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db)
):
    """List all teachers"""
    query = db.query(models.Teacher)
    if school_id:
        query = query.filter(models.Teacher.school_id == school_id)
    teachers = query.offset(pagination.skip).limit(pagination.limit).all()
    return teachers


@router.get("/{teacher_id}", response_model=schemas.Teacher)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Get teacher by ID"""
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise NotFoundException(f"Teacher with ID {teacher_id} not found")
    return teacher


@router.post("/", response_model=schemas.Teacher, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher_data: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """Create a new teacher"""
    # Check if employee ID already exists
    existing = db.query(models.Teacher).filter(
        models.Teacher.employee_id == teacher_data.employee_id
    ).first()
    if existing:
        raise ConflictException(f"Teacher with employee ID '{teacher_data.employee_id}' already exists")
    
    teacher = models.Teacher(**teacher_data.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.patch("/{teacher_id}", response_model=schemas.Teacher)
def update_teacher(
    teacher_id: int,
    teacher_data: schemas.TeacherUpdate,
    db: Session = Depends(get_db)
):
    """Update a teacher"""
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise NotFoundException(f"Teacher with ID {teacher_id} not found")
    
    update_data = teacher_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teacher, field, value)
    
    db.commit()
    db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Delete a teacher"""
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise NotFoundException(f"Teacher with ID {teacher_id} not found")
    
    db.delete(teacher)
    db.commit()
    return None
