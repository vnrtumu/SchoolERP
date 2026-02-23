import bcrypt

# Monkeypatch bcrypt to fix incompatibility with passlib 1.7.4+ and bcrypt 4.0.0+
if not hasattr(bcrypt, "__about__"):
    class About:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = About

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

# Global Exception Handler for debugging production 500s
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"❌ GLOBAL ERROR: {str(exc)}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_type": type(exc).__name__, "message": str(exc)}
    )

from fastapi import Request
from fastapi.responses import JSONResponse


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

from app.modules.schools.router_master import router as schools_master_router
app.include_router(schools_master_router, prefix="/api/v1/master/schools", tags=["Schools (Master)"])

from app.modules.plans.router import router as plans_router
app.include_router(plans_router, prefix="/api/v1/master/plans", tags=["Subscription Plans (Master)"])

from app.modules.notes.router import router as notes_router
app.include_router(notes_router, prefix="/api/v1/master/notes", tags=["Personal Notes (Master)"])

from app.modules.tickets.router import router as tickets_router
app.include_router(tickets_router, prefix="/api/v1/master/tickets", tags=["Support Tickets (Master)"])

from app.modules.branches.router import router as branches_router
app.include_router(branches_router, prefix="/api/v1/branches", tags=["Branches"])

from app.modules.branch_admin.router import router as branch_admin_router
app.include_router(branch_admin_router, prefix="/api/v1/branch", tags=["Branch Admin"])

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
