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
        # We need an administrative connection that is not bound to a specific DB 
        # to execute CREATE DATABASE. Since SQLALchemy async engines struggle with 
        # switching DB contexts mid-stream for DDL commands on MySQL, we will use
        # the standard root connection URL but omit the database name.
        
        # Parse the master URL. Example: mysql+aiomysql://root:password@localhost:3306/master_db
        # We strip off the /master_db part.
        base_url = settings.MASTER_DATABASE_URL.rsplit('/', 1)[0]
        
        # Create an engine connected to the MySQL server root
        connect_args = {}
        if "aivencloud" in base_url:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx
            
        admin_engine = create_async_engine(base_url, connect_args=connect_args, echo=False)
        
        async with admin_engine.begin() as conn:
            # Create the database. MySQL requires this to be outside a transaction
            # but SQLAlchemy handles basic DDL nicely if committed correctly.
            logger.info(f"Creating database {db_name}...")
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
            logger.info(f"Database {db_name} created successfully.")
            
        await admin_engine.dispose()
        return True
    except Exception as e:
        logger.error(f"Failed to create database {db_name}: {str(e)}")
        return False

def run_alembic_upgrade(db_url: str):
    """
    Runs Alembic migrations synchronously against the specified database URL.
    This must be run in a threadpool if invoked from an async FastAPI route.
    """
    try:
        # Find path to alembic.ini relative to the root project directory
        # The script is usually in app/tenancy/provisioning.py, we need to go up two levels
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        alembic_ini_path = os.path.join(project_root, 'alembic.ini')
        
        if not os.path.exists(alembic_ini_path):
            raise FileNotFoundError(f"alembic.ini not found at {alembic_ini_path}")

        # Setup Alembic Config
        alembic_cfg = Config(alembic_ini_path)
        
        # Override the sqlalchemy.url in the config to point to the new tenant DB
        # Format expects standard sync driver: mysql+pymysql://...
        sync_url = db_url.replace("mysql+aiomysql://", "mysql+pymysql://")
        
        # Escape % signs because ConfigParser uses them for string interpolation
        sync_url_escaped = sync_url.replace('%', '%%')
        
        alembic_cfg.set_main_option("sqlalchemy.url", sync_url_escaped)
        
        # Capture the URL in an environment variable for Alembic's env.py to pick up
        os.environ["CURRENT_TENANT_DB_URL"] = sync_url_escaped
        
        logger.info(f"Running Alembic migrations against {sync_url}...")
        
        # Run the upgrade
        command.upgrade(alembic_cfg, "head")
        
        logger.info(f"Alembic migrations completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to run Alembic migrations: {str(e)}")
        return False

async def provision_new_tenant(db_name: str) -> bool:
    """
    High-level orchestrator:
    1. Creates the raw MySQL database
    2. Constructs the new database connection string
    3. Runs Alembic migrations to build tables within it
    """
    # Step 1: Create Database
    success = await create_tenant_database(db_name)
    if not success:
        return False
        
    # Step 2: Formulate the connection string
    base_url = settings.MASTER_DATABASE_URL.rsplit('/', 1)[0]
    new_db_url = f"{base_url}/{db_name}"
    
    # Step 3: Run Alembic migrations (offloaded to threadpool to avoid blocking event loop)
    loop = asyncio.get_running_loop()
    migration_success = await loop.run_in_executor(None, run_alembic_upgrade, new_db_url)
    
    return migration_success
