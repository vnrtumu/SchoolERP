#!/usr/bin/env python
"""
Tenant Provisioning Script

Creates a new school (tenant) with isolated database.

Usage:
    python scripts/provision_tenant.py \\
        --subdomain greenwood \\
        --name "Greenwood International School" \\
        --code GIS001 \\
        --db-name greenwood_erp \\
        --db-user greenwood_admin \\
        --db-password SecurePassword123!
"""
import asyncio
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymysql
from sqlalchemy import select
from app.config import settings
from app.tenancy.database import get_master_session
from app.tenancy.models import School
from app.tenancy.encryption import encrypt_password
from app.shared.base_models import Base


async def create_mysql_database(db_host: str, db_port: int, db_name: str, root_password: str):
    """Create MySQL database for tenant"""
    try:
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user="root",
            password=root_password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✓ Database '{db_name}' created successfully")
        
        connection.commit()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        raise


async def provision_tenant(
    subdomain: str,
    name: str,
    code: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    root_password: str
):
    """Provision a new tenant"""
    print(f"\n{'='*60}")
    print(f"Provisioning Tenant: {name}")
    print(f"{'='*60}\n")
    
    # Step 1: Check if subdomain/code already exists
    print("Step 1: Checking for conflicts...")
    async with get_master_session() as session:
        result = await session.execute(
            select(School).where(
                (School.subdomain == subdomain) | (School.code == code)
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"✗ Tenant with subdomain '{subdomain}' or code '{code}' already exists")
            return False
    
    print("✓ No conflicts found")
    
    # Step 2: Create MySQL database
    print(f"\nStep 2: Creating database '{db_name}'...")
    await create_mysql_database(db_host, db_port, db_name, root_password)
    
    # Step 3: Register tenant in master registry
    print("\nStep 3: Registering tenant in master registry...")
    encrypted_password = encrypt_password(db_password)
    
    async with get_master_session() as session:
        school = School(
            subdomain=subdomain,
            name=name,
            code=code,
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password_encrypted=encrypted_password,
            is_active=True
        )
        session.add(school)
        await session.commit()
        await session.refresh(school)
        print(f"✓ Tenant registered with ID: {school.id}")
        tenant_id = school.id
    
    # Step 4: Run migrations on tenant database
    print("\nStep 4: Running migrations on tenant database...")
    print("NOTE: You need to run: alembic -c alembic/tenant/alembic.ini upgrade head")
    print(f"      with TENANT_DB_NAME={db_name} environment variable")
    
    # Step 5: Seed RBAC data
    print("\nStep 5: Seeding roles and permissions...")
    from app.tenancy.manager import connection_manager
    from app.rbac.engine import PermissionEngine
    
    # Get fresh school object
    async with get_master_session() as session:
        result = await session.execute(select(School).where(School.id == tenant_id))
        school = result.scalar_one()
    
    # Get tenant session
    session_maker = await connection_manager.get_session_maker(school)
    async with session_maker() as tenant_session:
        engine = PermissionEngine()
        await engine.seed_roles(tenant_session)
        print("✓ Roles and permissions seeded")
    
    print(f"\n{'='*60}")
    print("✅ Tenant provisioned successfully!")
    print(f"{'='*60}\n")
    print(f"Subdomain: {subdomain}")
    print(f"Database: {db_name}")
    print(f"Tenant ID: {tenant_id}")
    print("\nNext steps:")
    print(f"1. Access via: http://{subdomain}.yourdomain.com")
    print(f"2. Or use header: X-Tenant-ID: {tenant_id}")
    print(f"3. Create initial admin user for this school")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Provision a new tenant")
    parser.add_argument("--subdomain", required=True, help="Tenant subdomain (e.g., greenwood)")
    parser.add_argument("--name", required=True, help="School name")
    parser.add_argument("--code", required=True, help="School code")
    parser.add_argument("--db-host", default="localhost", help="Database host")
    parser.add_argument("--db-port", type=int, default=3306, help="Database port")
    parser.add_argument("--db-name", required=True, help="Database name")
    parser.add_argument("--db-user", default="root", help="Database user")
    parser.add_argument("--db-password", required=True, help="Database password")
    parser.add_argument("--root-password", required=True, help="MySQL root password")
    
    args = parser.parse_args()
    
    asyncio.run(provision_tenant(
        subdomain=args.subdomain,
        name=args.name,
        code=args.code,
        db_host=args.db_host,
        db_port=args.db_port,
        db_name=args.db_name,
        db_user=args.db_user,
        db_password=args.db_password,
        root_password=args.root_password
    ))


if __name__ == "__main__":
    main()
