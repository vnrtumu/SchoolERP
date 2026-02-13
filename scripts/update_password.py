import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.tenancy.database import get_master_session
from app.tenancy.models import SuperAdmin
from app.core.security import get_password_hash

async def update_password():
    username = "superadmin1"
    new_password = "testpassword123"
    
    print(f"Updating password for {username}...")
    
    async with get_master_session() as session:
        result = await session.execute(
            select(SuperAdmin).where(SuperAdmin.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User {username} not found!")
            return
            
        user.hashed_password = get_password_hash(new_password)
        await session.commit()
        
        print(f"✅ Password for '{username}' updated to '{new_password}'")

if __name__ == "__main__":
    asyncio.run(update_password())
