from sqlalchemy import String, Boolean, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_models import BaseModel
from app.shared.enums import UserRole
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.schools.models import School
    from app.modules.branches.models import Branch


class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Role and school association
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=True)
    
    # Branch assignment (for multi-branch support)
    primary_branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id"), 
        nullable=True,
        comment="Primary branch for branch-level roles (BRANCH_ADMIN, BRANCH_PRINCIPAL)"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="users")
    primary_branch: Mapped["Branch"] = relationship(
        "Branch", 
        foreign_keys=[primary_branch_id],
        lazy="joined"
    )
    # Multi-branch access (for users who work across multiple branches)
    # branches: Mapped[list["Branch"]] = relationship(
    #     "Branch",
    #     secondary="user_branches",
    #     back_populates="users"
    # )
    
    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"
