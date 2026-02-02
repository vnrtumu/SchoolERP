from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_models import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.schools.models import School


class Course(BaseModel):
    """Course/Subject model"""
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    
    # Course Information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Academic Details
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., Core, Elective
    
    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="courses")
    
    def __repr__(self) -> str:
        return f"<Course {self.name} ({self.code})>"
