#!/bin/sh
set -e
# If PORT is not set, default to 8000
: "${PORT:=8000}"

echo "Running migrations..."
# Force unbuffered Python output to catch tracebacks
export PYTHONUNBUFFERED=1

echo "Verifying database network connectivity before migrations..."
python3 -c "
import asyncio, ssl, sys, os
from sqlalchemy.ext.asyncio import create_async_engine
try:
    url = os.environ.get('MASTER_DATABASE_URL')
    if url:
        if 'ssl-mode=' in url: url = url[:url.find('?')]
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        engine = create_async_engine(url, connect_args={'ssl': ctx}, echo=True)
        async def go():
            async with engine.connect() as conn: pass
        asyncio.run(go())
        print('✅ Network connection successful')
except Exception as e:
    print(f'❌ Network Error: {e}', file=sys.stderr)
    sys.exit(1)
" || exit 1

# Run tenant migrations
if ! alembic upgrade head > alembic.log 2>&1; then
    echo "❌ Tenant migrations failed!"
    cat alembic.log
    exit 1
fi

# Run master migrations
if ! alembic -c alembic_master.ini upgrade head > alembic_master.log 2>&1; then
    echo "❌ Master migrations failed!"
    cat alembic_master.log
    exit 1
fi

echo "✅ Migrations completed successfully."
echo "Starting application on port $PORT..."
exec gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
