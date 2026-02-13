import asyncio
import sys
import secrets
import string
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.tenancy.database import get_master_session
from app.tenancy.models import SuperAdmin
from app.core.security import get_password_hash

def generate_password(length=16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))

async def create_superadmins():
    print(f"\n{'='*60}")
    print("Creating Superadmin Accounts")
    print(f"{'='*60}\n")
    
    superadmins_to_create = [
        {"username": "superadmin1", "email": "superadmin1@mindwhile.com", "full_name": "Super Admin One"},
        {"username": "superadmin2", "email": "superadmin2@mindwhile.com", "full_name": "Super Admin Two"}
    ]
    
    async with get_master_session() as session:
        for admin_data in superadmins_to_create:
            # Check if user already exists
            result = await session.execute(
                select(SuperAdmin).where(
                    (SuperAdmin.username == admin_data["username"]) | 
                    (SuperAdmin.email == admin_data["email"])
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⚠ Superadmin '{admin_data['username']}' already exists. Skipping.")
                continue
            
            # Generate password
            password = generate_password()
            hashed_password = get_password_hash(password)
            
            # Create user
            new_admin = SuperAdmin(
                username=admin_data["username"],
                email=admin_data["email"],
                hashed_password=hashed_password,
                full_name=admin_data["full_name"],
                is_active=True
            )
            
            session.add(new_admin)
            await session.commit()
            await session.refresh(new_admin)
            
            print(f"✅ Created Superadmin: {admin_data['username']}")
            print(f"   Email:    {admin_data['email']}")
            print(f"   Password: {password}")
            print("-" * 40)
            
    print("\nDone.")

if __name__ == "__main__":
    asyncio.run(create_superadmins())
