import asyncio
import ssl
from sqlalchemy.ext.asyncio import create_async_engine

async def test():
    try:
        print("Connecting...")
        ssl_context = ssl.create_default_context()
        import os
        url = os.environ.get("MASTER_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        engine = create_async_engine(
            url,
            connect_args={"ssl": ssl_context}
        )
        async with engine.connect() as conn:
            print('Connected!')
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
