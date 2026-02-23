from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import the Base and all models
from app.shared.base_models import Base, MasterBase
from app.config import settings

# Import all models to ensure they're registered
from app.modules.schools.models import School
from app.modules.branches.models import Branch
from app.modules.auth.models import User
from app.tenancy.models import SuperAdmin, SubscriptionPlan, Note
from app.modules.students.models import Student
from app.modules.teachers.models import Teacher
from app.modules.courses.models import Course

# this is the Alembic Config object
config = context.config

# Override the sqlalchemy.url to use the dynamic environment variable for production
if settings.MASTER_DATABASE_URL:
    escaped_url = settings.MASTER_DATABASE_URL.replace("%", "%%")
    # Workaround for aiomysql which doesn't support ssl-mode via query parameters directly in sqlalchemy
    if "ssl-mode=REQUIRED" in escaped_url:
        escaped_url = escaped_url.replace("?ssl-mode=REQUIRED", "").replace("&ssl-mode=REQUIRED", "")
    config.set_main_option("sqlalchemy.url", escaped_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

import ssl

async def run_async_migrations() -> None:
    url = config.get_main_option("sqlalchemy.url")
    connect_args = {}
    if url and "aivencloud" in url:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ctx

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
