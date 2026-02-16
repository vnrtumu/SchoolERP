from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.shared.base_models import BaseModel


# Association table for User-Branch many-to-many relationship
user_branches = Table(
    "user_branches",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("branch_id", Integer, ForeignKey("branches.id"), primary_key=True),
)


class Branch(BaseModel):
    """
    Branch/Campus within a school tenant.
    Allows multi-location schools to manage different physical locations.
    """
    __tablename__ = "branches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Branch identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Contact information
    address: Mapped[str] = mapped_column(Text, nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Branch status
    is_main_branch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships (to be added when other models are updated)
    # users = relationship("User", back_populates="branches", secondary=user_branches)
    
    def __repr__(self) -> str:
        return f"<Branch {self.name} ({self.code})>"
