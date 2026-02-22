from sqlalchemy import String, Integer, Boolean, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.shared.base_models import Base, MasterBase


class School(MasterBase):
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


class SuperAdmin(MasterBase):
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
    
    # Profile & Address Data
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    position: Mapped[str] = mapped_column(String(100), nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    state: Mapped[str] = mapped_column(String(200), nullable=True)
    pin: Mapped[str] = mapped_column(String(20), nullable=True)
    zip: Mapped[str] = mapped_column(String(20), nullable=True)
    tax_no: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Social URLs
    facebook_url: Mapped[str] = mapped_column(String(255), nullable=True)
    twitter_url: Mapped[str] = mapped_column(String(255), nullable=True)
    github_url: Mapped[str] = mapped_column(String(255), nullable=True)
    dribbble_url: Mapped[str] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<SuperAdmin {self.username}>"


class SubscriptionPlan(MasterBase):
    """
    Subscription Plans available for Schools (Tenants).
    Stored in the master database.
    """
    __tablename__ = "subscription_plans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    max_students: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_price: Mapped[float] = mapped_column(nullable=False)
    yearly_price: Mapped[float] = mapped_column(nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
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
        return f"<SubscriptionPlan {self.plan_name}>"


class Note(MasterBase):
    """
    Personal Sticky Notes assigned to SuperAdmins.
    Stored in the master database.
    """
    __tablename__ = "notes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("super_admins.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(String(50), default="primary", nullable=False)
    datef: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
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
        return f"<Note {self.id} (user_id={self.user_id})>"


class Ticket(MasterBase):
    """
    Support tickets managed by SuperAdmins.
    Stored in the master database.
    """
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("super_admins.id", ondelete="CASCADE"), index=True, nullable=False)
    
    ticketTitle: Mapped[str] = mapped_column(String(255), nullable=False)
    ticketDescription: Mapped[str] = mapped_column(Text, nullable=False)
    Status: Mapped[str] = mapped_column(String(50), default="Open", nullable=False)
    Label: Mapped[str] = mapped_column(String(50), default="success", nullable=False)
    thumb: Mapped[str] = mapped_column(String(500), nullable=True)
    AgentName: Mapped[str] = mapped_column(String(100), nullable=False)
    
    Date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Ticket {self.id} (user_id={self.user_id})>"
