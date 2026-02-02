import json
from typing import Optional
import redis.asyncio as aioredis
from app.config import settings
from app.tenancy.models import School

class TenantCache:
    """Redis-based tenant metadata caching"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._cache_ttl = 3600  # 1 hour
    
    async def connect(self):
        """Initialize Redis connection"""
        self.redis = await aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    def _serialize_school(self, school: School) -> str:
        """Serialize school object to JSON"""
        return json.dumps({
            "id": school.id,
            "subdomain": school.subdomain,
            "name": school.name,
            "code": school.code,
            "db_host": school.db_host,
            "db_port": school.db_port,
            "db_name": school.db_name,
            "db_user": school.db_user,
            "db_password_encrypted": school.db_password_encrypted,
            "is_active": school.is_active
        })
    
    def _deserialize_school(self, data: str) -> dict:
        """Deserialize JSON to school dict"""
        return json.loads(data)
    
    async def get_tenant(self, subdomain: str) -> Optional[dict]:
        """Get tenant by subdomain from cache"""
        if not self.redis:
            return None
        
        key = f"tenant:subdomain:{subdomain}"
        data = await self.redis.get(key)
        
        if data:
            return self._deserialize_school(data)
        return None
    
    async def set_tenant(self, subdomain: str, school: School):
        """Cache tenant by subdomain"""
        if not self.redis:
            return
        
        key = f"tenant:subdomain:{subdomain}"
        data = self._serialize_school(school)
        await self.redis.setex(key, self._cache_ttl, data)
    
    async def get_tenant_by_id(self, tenant_id: int) -> Optional[dict]:
        """Get tenant by ID from cache"""
        if not self.redis:
            return None
        
        key = f"tenant:id:{tenant_id}"
        data = await self.redis.get(key)
        
        if data:
            return self._deserialize_school(data)
        return None
    
    async def set_tenant_by_id(self, tenant_id: int, school: School):
        """Cache tenant by ID"""
        if not self.redis:
            return
        
        key = f"tenant:id:{tenant_id}"
        data = self._serialize_school(school)
        await self.redis.setex(key, self._cache_ttl, data)
    
    async def invalidate_tenant(self, subdomain: str, tenant_id: int):
        """Invalidate tenant cache"""
        if not self.redis:
            return
        
        await self.redis.delete(
            f"tenant:subdomain:{subdomain}",
            f"tenant:id:{tenant_id}"
        )


# Global cache instance
tenant_cache = TenantCache()
