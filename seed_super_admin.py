import asyncio
from app.tenancy.database import MasterSessionLocal
from app.tenancy.models import SuperAdmin
from app.core.security import get_password_hash

async def seed():
    async with MasterSessionLocal() as db:
        user = SuperAdmin(
            email="superadmin@example.com",
            username="superadmin1",
            hashed_password=get_password_hash("testpassword123"),
            full_name="Venkata Narayana",
            is_active=True
        )
        db.add(user)
        await db.commit()
        print("SuperAdmin seeded successfully!")

asyncio.run(seed())
