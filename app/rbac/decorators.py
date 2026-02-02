from functools import wraps
from typing import List, Callable
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.rbac.constants import Permission, Role
from app.rbac.engine import PermissionEngine


def require_permissions(*required_permissions: str):
    """
    Decorator to enforce permissions on endpoint functions.
    
    Usage:
        @router.post("/students")
        @require_permissions(Permission.STUDENTS_CREATE)
        async def create_student(
            student_data: StudentCreate,
            db: AsyncSession = Depends(get_tenant_db),
            current_user = Depends(get_current_user)
        ):
            ...
    
    Args:
        *required_permissions: One or more permission codes required
    
    Raises:
        HTTPException(403): If user lacks required permissions
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs (must be injected by Depends)
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )
            
            # Extract database session
            db = kwargs.get("db")
            if not db:
                raise HTTPException(
                    status_code=500,
                    detail="Database session not available"
                )
            
            # Check permissions
            engine = PermissionEngine()
            has_permission = await engine.check_user_permissions(
                db,
                current_user,
                list(required_permissions)
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing required permissions: {', '.join(required_permissions)}"
                )
            
            # Execute the wrapped function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*required_permissions: str):
    """
    Decorator that requires ANY ONE of the specified permissions (OR logic).
    
    Usage:
        @require_any_permission(Permission.FEES_VIEW, Permission.FEES_COLLECT)
        async def view_fees(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(401, "Authentication required")
            
            db = kwargs.get("db")
            if not db:
                raise HTTPException(500, "Database session not available")
            
            engine = PermissionEngine()
            
            # Check if user has ANY of the permissions
            for perm in required_permissions:
                if await engine.check_user_permissions(db, current_user, [perm]):
                    return await func(*args, **kwargs)
            
            raise HTTPException(
                status_code=403,
                detail=f"Requires at least one of: {', '.join(required_permissions)}"
            )
        
        return wrapper
    return decorator


def require_role(*required_roles: str):
    """
    Decorator to enforce role-based access.
    
    Usage:
        @require_role(Role.SCHOOL_ADMIN, Role.PRINCIPAL)
        async def manage_school(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(401, "Authentication required")
            
            # Check if user has any of the required roles
            user_role = getattr(current_user, "role", None)
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires role: {', '.join(required_roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
