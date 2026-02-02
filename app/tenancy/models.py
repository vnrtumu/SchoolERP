from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.shared.base_models import Base


class School(Base):
    """
    Master registry of all schools (tenants).
    Each school has its own isolated database.
    """
    __tablename__ = "schools"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Tenant identification
    subdomain: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Database connection details
    db_host: Mapped[str] = mapped_column(String(255), nullable=False, default="localhost")
    db_port: Mapped[int] = mapped_column(Integer, nullable=False, default=3306)
    db_name: Mapped[str] = mapped_column(String(100), nullable=False)
    db_user: Mapped[str] = mapped_column(String(100), nullable=False)
    db_password_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Subscription & limits
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    max_students: Mapped[int] = mapped_column(Integer, nullable=True)
    max_teachers: Mapped[int] = mapped_column(Integer, nullable=True)
    subscription_tier: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Contact information
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<School {self.name} ({self.subdomain})>"


class SuperAdmin(Base):
    """
    Global super administrators with cross-tenant access.
    Stored in master database, not tenant databases.
    """
    __tablename__ = "super_admins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<SuperAdmin {self.username}>"
