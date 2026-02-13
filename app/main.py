from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Import tenant cache for startup/shutdown
from app.tenancy.cache import tenant_cache
from app.tenancy.manager import connection_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    print("🚀 Starting Mindwhile ERP - Multi-Tenant Architecture")
    print(f"📊 Master DB: {settings.MASTER_DATABASE_URL.split('@')[-1]}")
    print(f"🔴 Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    
    # Initialize Redis connection
    await tenant_cache.connect()
    print("✅ Redis cache connected")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await tenant_cache.disconnect()
    await connection_manager.close_all()
    print("✅ All connections closed")


# Create FastAPI app
app = FastAPI(
    title="Mindwhile ERP - Multi-Tenant",
    description="Enterprise Multi-School ERP with Database-per-School Isolation",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Mindwhile ERP",
        "version": "2.0.0",
        "architecture": "Multi-Tenant (Database-per-School)",
        "docs": "/docs",
        "features": {
            "tenant_resolution": ["subdomain", "header"],
            "caching": "Redis",
            "rbac": "40+ permissions, 8 roles",
            "isolation": "Physical database per school"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "redis": "connected" if tenant_cache.redis else "disconnected",
        "version": "2.0.0"
    }


# Note: Module routers will be added here after async conversion
# Example:
# from app.modules.students.router import router as students_router
# app.include_router(students_router, prefix="/api/v1/students", tags=["Students"])

from app.modules.super_admin.router import router as super_admin_router
app.include_router(super_admin_router, prefix="/api/v1/super-admin", tags=["Super Admin"])

print("\n" + "="*60)
print("🏫 Mindwhile ERP - Multi-Tenant Architecture v2.0")
print("="*60)
print("\n📚 API Documentation:")
print("   Swagger UI: http://localhost:8000/docs")
print("   ReDoc:      http://localhost:8000/redoc")
print("\n🔧 Tenant Resolution:")
print("   Header: X-Tenant-ID or X-Tenant-Subdomain")
print("   Subdomain: schoolname.erp.com")
print("\n⚠️  Note: Existing modules need async conversion")
print("   Core infrastructure is ready for integration")
print("="*60 + "\n")
