import asyncio
from sqlalchemy import text
from app.tenancy.database import SessionLocalMaster

async def fix():
    async with SessionLocalMaster() as db:
        await db.execute(text("UPDATE alembic_version SET version_num = '9400fce0d339'"))
        await db.commit()
        print("Updated alembic_version to 9400fce0d339")

asyncio.run(fix())
