import asyncio
import os
import ssl
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

import sys

import bcrypt

async def reset_and_seed():
    from app.config import settings
    url = settings.MASTER_DATABASE_URL
    os.environ['MASTER_DATABASE_URL'] = url
        
    print(f"Connecting to Aiven: {url}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    engine = create_async_engine(url, connect_args={'ssl': ctx}, echo=False)
    
    print("Seeding Super Admin...")
    from app.tenancy.models import SuperAdmin
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        # Check if exists
        from sqlalchemy import select
        res = await session.execute(select(SuperAdmin).filter_by(username="admin"))
        admin = res.scalar_one_or_none()
        if not admin:
            # Manually hash with bcrypt to bypass passlib bug
            salt = bcrypt.gensalt()
            pwd = bcrypt.hashpw(b"admin123", salt).decode("utf-8")
            
            admin = SuperAdmin(
                email="admin@mindwhile.com",
                username="admin",
                hashed_password=pwd,
                full_name="System Administrator",
                is_active=True
            )
            session.add(admin)
            await session.commit()
            print("Super Admin created: admin / admin123")
        else:
            print("Super Admin already exists.")
            
    await engine.dispose()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(reset_and_seed())
