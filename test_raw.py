import asyncio
import ssl
from sqlalchemy.ext.asyncio import create_async_engine

async def test_ssl_injection():
    try:
        import os
        url = os.environ.get("MASTER_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connect_args = {"ssl": ctx}
        
        engine = create_async_engine(url, connect_args=connect_args)
        print("Engine created. Attempting connect...")
        
        async with engine.connect() as conn:
            print("Engine connected successfully!")
            
    except Exception as e:
        print(f"Exception: {type(e).__name__} - {e}")

asyncio.run(test_ssl_injection())
