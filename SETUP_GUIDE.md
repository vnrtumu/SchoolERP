# Multi-Tenant ERP Setup Guide

## Quick Start (5 Steps)

### 1. Generate Encryption Key
```bash
python scripts/generate_key.py
```
Copy the key to `.env` as `TENANT_PASSWORD_ENCRYPTION_KEY`

### 2. Create Master Database
```bash
python create_master_database.py
```

### 3. Run Master DB Migrations
```bash
alembic -c alembic_master.ini upgrade head
```

### 4. Start Redis (Required)
```bash
redis-server
# OR if using Homebrew on Mac:
brew services start redis
```

### 5. Provision First Tenant
```bash
python scripts/provision_tenant.py \
    --subdomain school1 \
    --name "First School" \
    --code SCH001 \
    --db-name school1_erp \
    --db-user root \
    --db-password "YourDBPassword" \
    --root-password "YourMySQLRootPassword"
```

## Architecture Summary

```
┌──────────────┐
│   Request    │ (schoola.erp.com OR X-Tenant-ID: 1)
└──────┬───────┘
       │
┌──────▼───────────────────────────────────┐
│  FastAPI: Tenant Resolver Middleware     │
│  1. Extract subdomain/header             │
│  2. Check Redis cache (< 10ms)           │
│  3. Fallback to master DB if needed      │
└──────┬───────────────────────────────────┘
       │
┌──────▼───────────────────────────────────┐
│  Connection Manager                      │
│  - Get/create engine for school          │
│  - 20 pooled connections per tenant      │
└──────┬───────────────────────────────────┘
       │
┌──────▼───────────────────────────────────┐
│  get_tenant_db() Dependency              │
│  - Scoped session to tenant's DB         │
│  - Auto commit/rollback                  │
│  - Tenant context in session.info        │
└──────────────────────────────────────────┘
```

## File Structure Created

```
app/
├── tenancy/               # Multi-tenancy engine
│   ├── models.py          # School, SuperAdmin
│   ├── database.py        # get_tenant_db, get_master_db
│   ├── resolver.py        # Tenant resolution
│   ├── manager.py         # Connection pooling  
│   ├── cache.py           # Redis caching
│   ├── encryption.py      # Password encryption
│   └── schemas.py         # Tenant schemas
│
├── rbac/                  # permission system
│   ├── constants.py       # 40+ permissions, 8 roles
│   ├── models.py          # Role, Permission models
│   ├── decorators.py      # @require_permissions
│   └── engine.py          # Permission evaluation
│
scripts/
├── provision_tenant.py    # Create new school
└── generate_key.py        # Encryption key generator

alembic_master/            # Master DB migrations
└── versions/

alembic_tenant/            # Tenant DB migrations  
└── versions/
```

## Using in Your Code

### Dependency Injection
```python
from app.tenancy.database import get_tenant_db
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/students")
async def list_students(
    db: AsyncSession = Depends(get_tenant_db)
):
    # db is automatically scoped to the correct tenant's database
    result = await db.execute(select(Student))
    return result.scalars().all()
```

### Permission Protection
```python
from app.rbac.decorators import require_permissions
from app.rbac.constants import Permission

@router.post("/students")
@require_permissions(Permission.STUDENTS_CREATE)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user = Depends(get_current_user)
):
    # Only users with students.create permission can access
    ...
```

## Testing

### Access Tenant A
```bash
curl -H "X-Tenant-Subdomain: school1" \
     http://localhost:8000/api/v1/students
```

### Access Tenant B
```bash
curl -H "X-Tenant-Subdomain: school2" \
     http://localhost:8000/api/v1/students
```

## Key Benefits

✅ **Complete Isolation**: No possibility of cross-tenant data leaks  
✅ **Independent Scaling**: Scale databases per school  
✅ **Regulatory Compliance**: Data residency per institution  
✅ **Performance**: Cached resolution + connection pooling  
✅ **Zero Downtime**: Add tenants without restarting  

## Dependencies Added

- `aiomysql==0.3.2` - Async MySQL driver
- `redis==7.1.0` - Caching layer
- `aioredis==2.0.1` - Async Redis client  
- `cryptography==44.0.0` - Password encryption

## Environment Variables

```env
# Master Database
MASTER_DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/master_registry

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Encryption (generated via scripts/generate_key.py)
TENANT_PASSWORD_ENCRYPTION_KEY=<generated-key>
```

## Next Steps

1. ✅ Core infrastructure complete
2. ⏳ Update existing modules to use async patterns
3. ⏳ Implement tenant-specific migrations
4. ⏳ Add parallel migration runner
5. ⏳ Create super admin management endpoints
6. ⏳ Test with multiple tenants
