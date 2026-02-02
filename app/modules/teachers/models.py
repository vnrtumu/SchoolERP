from sqlalchemy import String, Integer, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from app.shared.base_models import BaseModel
from app.shared.enums import Gender
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.schools.models import School


class Teacher(BaseModel):
    """Teacher model"""
    __tablename__ = "teachers"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    
    # Personal Information
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[Gender] = mapped_column(SQLEnum(Gender), nullable=False)
    
    # Contact Information
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Employment Information
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    designation: Mapped[str] = mapped_column(String(100), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    qualification: Mapped[str] = mapped_column(String(200), nullable=True)
    specialization: Mapped[str] = mapped_column(String(200), nullable=True)
    
    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="teachers")
    
    def __repr__(self) -> str:
        return f"<Teacher {self.first_name} {self.last_name} ({self.employee_id})>"
