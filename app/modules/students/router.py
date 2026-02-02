from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.modules.students import schemas, models
from app.core.dependencies import Pagination
from app.core.exceptions import NotFoundException, ConflictException

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=list[schemas.Student])
def list_students(
    school_id: Optional[int] = None,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db)
):
    """List all students"""
    query = db.query(models.Student)
    if school_id:
        query = query.filter(models.Student.school_id == school_id)
    students = query.offset(pagination.skip).limit(pagination.limit).all()
    return students


@router.get("/{student_id}", response_model=schemas.Student)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get student by ID"""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise NotFoundException(f"Student with ID {student_id} not found")
    return student


@router.post("/", response_model=schemas.Student, status_code=status.HTTP_201_CREATED)
def create_student(student_data: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Create a new student"""
    # Check if admission number already exists
    existing = db.query(models.Student).filter(
        models.Student.admission_number == student_data.admission_number
    ).first()
    if existing:
        raise ConflictException(f"Student with admission number '{student_data.admission_number}' already exists")
    
    student = models.Student(**student_data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.patch("/{student_id}", response_model=schemas.Student)
def update_student(
    student_id: int,
    student_data: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    """Update a student"""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise NotFoundException(f"Student with ID {student_id} not found")
    
    update_data = student_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student"""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise NotFoundException(f"Student with ID {student_id} not found")
    
    db.delete(student)
    db.commit()
    return None
