"""
Legacy database module - DEPRECATED

This file has been replaced by the multi-tenant architecture:
- Master DB: app/tenancy/database.py -> get_master_db()
- Tenant DBs: app/tenancy/database.py -> get_tenant_db()

DO NOT USE THIS FILE. It is kept for reference only.
"""

# For backwards compatibility during migration, re-export from new location
from app.shared.base_models import Base
from app.tenancy.database import get_tenant_db as get_db, get_master_db

__all__ = ["Base", "get_db", "get_master_db"]
