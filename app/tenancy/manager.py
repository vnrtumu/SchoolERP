from typing import Dict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from app.tenancy.models import School
from app.tenancy.encryption import decrypt_password


class ConnectionManager:
    """
    Manages per-tenant database connections with pooling.
    
    Each tenant (school) gets its own connection pool to its isolated database.
    Connections are cached and reused for performance.
    """
    
    def __init__(self):
        self._engines: Dict[int, AsyncEngine] = {}
        self._session_makers: Dict[int, async_sessionmaker] = {}
    
    def _build_connection_string(self, school: School) -> str:
        """Build async MySQL connection string for tenant"""
        password = decrypt_password(school.db_password_encrypted)
        
        # URL-encode special characters in password
        from urllib.parse import quote_plus
        password_encoded = quote_plus(password)
        
        return (
            f"mysql+aiomysql://{school.db_user}:{password_encoded}"
            f"@{school.db_host}:{school.db_port}/{school.db_name}"
            f"?charset=utf8mb4"
        )
    
    async def get_engine(self, school: School) -> AsyncEngine:
        """Get or create async engine for tenant"""
        if school.id not in self._engines:
            connection_string = self._build_connection_string(school)
            
            engine_kwargs = {
                "pool_size": 20,
                "max_overflow": 10,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
                "echo": False
            }
            
            if "aivencloud" in connection_string:
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                engine_kwargs["connect_args"] = {"ssl": ctx}
                
            self._engines[school.id] = create_async_engine(
                connection_string,
                **engine_kwargs
            )
        
        return self._engines[school.id]
    
    async def get_session_maker(self, school: School) -> async_sessionmaker:
        """Get or create async session maker for tenant"""
        if school.id not in self._session_makers:
            engine = await self.get_engine(school)
            
            self._session_makers[school.id] = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
        
        return self._session_makers[school.id]
    
    async def close_all(self):
        """Close all tenant engine connections (for graceful shutdown)"""
        for engine in self._engines.values():
            await engine.dispose()
        
        self._engines.clear()
        self._session_makers.clear()
    
    async def close_tenant(self, tenant_id: int):
        """Close connection for specific tenant (useful for maintenance)"""
        if tenant_id in self._engines:
            await self._engines[tenant_id].dispose()
            del self._engines[tenant_id]
            del self._session_makers[tenant_id]


# Global connection manager instance
connection_manager = ConnectionManager()
