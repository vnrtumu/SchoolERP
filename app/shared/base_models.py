from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


# Base class for all ORM models (both master and tenant databases)
class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models (Tenant DBs)"""
    pass


class MasterBase(DeclarativeBase):
    """Declarative base for Master Database models"""
    pass


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
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


class BaseModel(Base, TimestampMixin):
    """Abstract base model with timestamps for tenant databases"""
    __abstract__ = True
