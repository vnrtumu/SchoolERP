from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from app.tenancy.resolver import tenant_resolver
from app.tenancy.manager import connection_manager
from app.tenancy.models import School

import ssl

master_engine_kwargs = {
    "pool_size": 20,
    "max_overflow": 10,
    "pool_pre_ping": True,
    "echo": settings.DEBUG
}

if settings.MASTER_DATABASE_URL and "aivencloud" in settings.MASTER_DATABASE_URL:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    master_engine_kwargs["connect_args"] = {"ssl": ctx}

# Master database engine (Control Plane)
master_engine = create_async_engine(
    settings.MASTER_DATABASE_URL,
    **master_engine_kwargs
)

# Master database session maker
MasterSessionLocal = async_sessionmaker(
    master_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


@asynccontextmanager
async def get_master_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for master database session.
    Useful for background tasks where Depends(get_master_db) is not available.
    """
    async with MasterSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_master_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for master database session.
    """
    async with get_master_session() as session:
        yield session


@asynccontextmanager
async def get_master_session():
    """
    Context manager for master DB session (for use outside request context).
    
    Usage:
        async with get_master_session() as session:
            result = await session.execute(...)
    """
    async with MasterSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_tenant_db(
    request: Request,
    master_session: AsyncSession = Depends(get_master_db)
) -> AsyncGenerator[AsyncSession, None]:
    """
    **PRIMARY DEPENDENCY** for tenant-scoped database session.
    
    This is the core of the multi-tenancy architecture. It:
    1. Resolves the tenant from the request (subdomain or header)
    2. Gets the appropriate database connection for that tenant
    3. Provides an isolated session to that tenant's database
    4. Prevents cross-database queries
    
    Use this in ALL tenant-specific endpoints:
        @router.get("/students")
        async def list_students(db: AsyncSession = Depends(get_tenant_db)):
            ...
    
    The session will automatically:
    - Connect to the correct tenant database
    - Include tenant context in session.info
    - Commit on success, rollback on error
    - Close properly
    """
    # Resolve tenant from request
    school: School = await tenant_resolver.resolve(request, master_session)
    
    # Get session maker for this specific tenant
    session_maker = await connection_manager.get_session_maker(school)
    
    # Create scoped session
    async with session_maker() as session:
        try:
            # Store tenant context in session for audit trails
            session.info["tenant_id"] = school.id
            session.info["tenant_name"] = school.name
            session.info["tenant_subdomain"] = school.subdomain
            
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_tenant(
    request: Request,
    master_session: AsyncSession = Depends(get_master_db)
) -> School:
    """
    Dependency to get current tenant metadata without database session.
    
    Use when you need tenant info but don't need database access:
        @router.get("/tenant-info")
        async def get_info(school: School = Depends(get_current_tenant)):
            return {"name": school.name}
    """
    return await tenant_resolver.resolve(request, master_session)
