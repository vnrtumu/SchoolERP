import asyncio
import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://mindwhile:mindwhile@localhost:5432/mindwhile_master"
from sqlalchemy import select
from app.tenancy.database import SessionLocalMaster
from app.tenancy.models import SuperAdmin

async def test():
    async with SessionLocalMaster() as db:
        result = await db.execute(
            select(SuperAdmin).where(SuperAdmin.id == 1)
        )
        user = result.scalar_one_or_none()
        print(f"User: {user}")

asyncio.run(test())
