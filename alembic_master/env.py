from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import master DB models
from app.shared.base_models import MasterBase
from app.tenancy.models import School, SuperAdmin
from app.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use URL from config or fallback to .ini
if settings.MASTER_DATABASE_URL:
    escaped_url = settings.MASTER_DATABASE_URL.replace("%", "%%")
    # Workaround for aiomysql which doesn't support ssl-mode via query parameters directly in sqlalchemy
    if "ssl-mode=REQUIRED" in escaped_url:
        escaped_url = escaped_url.replace("?ssl-mode=REQUIRED", "").replace("&ssl-mode=REQUIRED", "")
    config.set_main_option("sqlalchemy.url", escaped_url)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = MasterBase.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table="alembic_master_version"
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        version_table="alembic_master_version"
    )

    with context.begin_transaction():
        context.run_migrations()


import ssl

async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context."""

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
