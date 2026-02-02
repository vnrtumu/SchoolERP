from typing import Optional
from fastapi import Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.tenancy.cache import tenant_cache
from app.tenancy.models import School


class TenantResolver:
    """Resolves tenant from request context (subdomain or header)"""
    
    async def resolve_from_subdomain(
        self,
        request: Request,
        master_session: AsyncSession
    ) -> Optional[School]:
        """Extract tenant from subdomain"""
        host = request.headers.get("host", "")
        
        # Handle localhost development
        if "localhost" in host or "127.0.0.1" in host:
            # For local development, check X-Tenant-Subdomain header
            subdomain = request.headers.get("X-Tenant-Subdomain")
            if not subdomain:
                return None
        else:
            # Production: extract subdomain from host
            parts = host.split(".")
            if len(parts) < 2:
                return None
            subdomain = parts[0]
        
        if not subdomain:
            return None
        
        # Check cache first
        cached_data = await tenant_cache.get_tenant(subdomain)
        if cached_data:
            # Reconstruct School object from cached data
            school = School()
            for key, value in cached_data.items():
                setattr(school, key, value)
            return school
        
        # Fallback to master DB
        result = await master_session.execute(
            select(School).where(School.subdomain == subdomain)
        )
        school = result.scalar_one_or_none()
        
        if school:
            await tenant_cache.set_tenant(subdomain, school)
        
        return school
    
    async def resolve_from_header(
        self,
        request: Request,
        master_session: AsyncSession
    ) -> Optional[School]:
        """Extract tenant from X-Tenant-ID header"""
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            return None
        
        try:
            tenant_id_int = int(tenant_id)
        except ValueError:
            return None
        
        # Check cache
        cached_data = await tenant_cache.get_tenant_by_id(tenant_id_int)
        if cached_data:
            school = School()
            for key, value in cached_data.items():
                setattr(school, key, value)
            return school
        
        # Fallback to master DB
        result = await master_session.execute(
            select(School).where(School.id == tenant_id_int)
        )
        school = result.scalar_one_or_none()
        
        if school:
            await tenant_cache.set_tenant_by_id(tenant_id_int, school)
        
        return school
    
    async def resolve(
        self,
        request: Request,
        master_session: AsyncSession
    ) -> School:
        """Primary resolution method with fallback strategy"""
        # Try subdomain first
        school = await self.resolve_from_subdomain(request, master_session)
        
        # Fallback to header
        if not school:
            school = await self.resolve_from_header(request, master_session)
        
        if not school:
            raise HTTPException(
                status_code=400,
                detail="Unable to identify tenant. Use subdomain or X-Tenant-ID header."
            )
        
        if not school.is_active:
            raise HTTPException(
                status_code=403,
                detail=f"Tenant '{school.name}' is currently inactive"
            )
        
        return school


# Global resolver instance
tenant_resolver = TenantResolver()
