from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException

# HTTP Bearer token authentication
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Get current user ID from JWT token"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise UnauthorizedException(detail="Invalid authentication credentials")
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(detail="Invalid authentication credentials")
    
    return user_id


def get_current_school_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[int]:
    """Get current school ID from JWT token (for multi-tenancy)"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise UnauthorizedException(detail="Invalid authentication credentials")
    
    school_id: Optional[int] = payload.get("school_id")
    return school_id


class Pagination:
    """Pagination dependency"""
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = min(limit, 100)  # Max 100 items per page
