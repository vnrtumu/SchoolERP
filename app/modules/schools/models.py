from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_models import BaseModel


class School(BaseModel):
    """School model - Foundation for multi-tenancy"""
    __tablename__ = "schools"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Contact Information
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    website: Mapped[str] = mapped_column(String(200), nullable=True)
    
    # Address
    address: Mapped[str] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # Configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="school")
    students: Mapped[list["Student"]] = relationship("Student", back_populates="school")
    teachers: Mapped[list["Teacher"]] = relationship("Teacher", back_populates="school")
    courses: Mapped[list["Course"]] = relationship("Course", back_populates="school")
    
    def __repr__(self) -> str:
        return f"<School {self.name} ({self.code})>"
