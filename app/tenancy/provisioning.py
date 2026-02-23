import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from alembic.config import Config
from alembic import command
import logging

from app.config import settings
from app.tenancy.database import master_engine

logger = logging.getLogger(__name__)

async def create_tenant_database(db_name: str) -> bool:
    """
    Connects to the MySQL instance using the master database credentials 
    and issues a CREATE DATABASE command for the new tenant.
    """
    try:
        # For Aiven/MySQL, we often need to connect to an existing DB first
        # to execute administrative commands. We'll use the base URL but
        # ensure it's pointing to the server root or 'defaultdb'.
        
        # Parse the master URL.
        full_url = settings.MASTER_DATABASE_URL
        if "aivencloud" in full_url:
            # Connect to 'defaultdb' instead of just the root to be safer with some drivers
            base_url = full_url.rsplit('/', 1)[0] + "/defaultdb"
        else:
            base_url = full_url.rsplit('/', 1)[0]
        
        print(f"DEBUG: Provisioning - Connecting to {base_url} to create {db_name}")
        
        connect_args = {}
        if "aivencloud" in base_url:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx
            
        admin_engine = create_async_engine(base_url, connect_args=connect_args, echo=True)
        
        async with admin_engine.begin() as conn:
            print(f"DEBUG: Executing CREATE DATABASE IF NOT EXISTS `{db_name}`")
            # We use isolation_level="AUTOCOMMIT" if possible, but begin() should work for simple DDL
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
            
        await admin_engine.dispose()
        print(f"DEBUG: Database {db_name} created or verified successfully.")
        return True
    except Exception as e:
        import traceback
        print(f"❌ ERROR: Failed to create database {db_name}")
        print(traceback.format_exc())
        logger.error(f"Failed to create database {db_name}: {str(e)}")
        return False

def run_alembic_upgrade(db_url: str):
    """
    Runs Alembic migrations synchronously against the specified database URL.
    This must be run in a threadpool if invoked from an async FastAPI route.
    """
    try:
        # Find path to alembic.ini relative to the root project directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        alembic_ini_path = os.path.join(project_root, 'alembic.ini')
        
        if not os.path.exists(alembic_ini_path):
            raise FileNotFoundError(f"alembic.ini not found at {alembic_ini_path}")

        # Setup Alembic Config
        alembic_cfg = Config(alembic_ini_path)
        
        # USE aiomysql since env.py is set up for async!
        # Do NOT replace with pymysql as it is not installed.
        sync_url = db_url 
        
        # Escape % signs because ConfigParser uses them for string interpolation
        sync_url_escaped = sync_url.replace('%', '%%')
        
        alembic_cfg.set_main_option("sqlalchemy.url", sync_url_escaped)
        os.environ["CURRENT_TENANT_DB_URL"] = sync_url_escaped
        
        print(f"DEBUG: Running Alembic upgrade on {sync_url}")
        
        # Run the upgrade
        command.upgrade(alembic_cfg, "head")
        
        print(f"DEBUG: Alembic migrations completed successfully for {db_url}")
        return True
    except Exception as e:
        import traceback
        print(f"❌ ERROR: Failed to run Alembic migrations for {db_url}")
        print(traceback.format_exc())
        logger.error(f"Failed to run Alembic migrations: {str(e)}")
        return False

async def provision_new_tenant(db_name: str) -> bool:
    """
    High-level orchestrator:
    1. Creates the raw MySQL database
    2. Constructs the new database connection string
    3. Runs Alembic migrations to build tables within it
    """
    print(f"DEBUG: Starting provisioning for tenant database: {db_name}")
    
    # Step 1: Create Database
    success = await create_tenant_database(db_name)
    if not success:
        return False
        
    # Step 2: Formulate the connection string
    base_url = settings.MASTER_DATABASE_URL.rsplit('/', 1)[0]
    new_db_url = f"{base_url}/{db_name}"
    
    # Step 3: Run Alembic migrations (offloaded to threadpool to avoid blocking event loop)
    # We use a threadpool because command.upgrade is a blocking sync call
    # even though env.py might be running async internally via asyncio.run
    loop = asyncio.get_running_loop()
    migration_success = await loop.run_in_executor(None, run_alembic_upgrade, new_db_url)
    
    if migration_success:
        print(f"✅ SUCCESSFULLY provisioned tenant: {db_name}")
    else:
        print(f"❌ FAILED to provision tenant: {db_name}")
        
    return migration_success
