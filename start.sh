#!/bin/sh
set -e
# If PORT is not set, default to 8000
: "${PORT:=8000}"

echo "Running migrations..."
# Force unbuffered Python output to catch tracebacks
export PYTHONUNBUFFERED=1

# Run tenant migrations
if ! alembic upgrade head 2>&1 | tee alembic.log; then
    echo "❌ Tenant migrations failed!"
    cat alembic.log
    exit 1
fi

# Run master migrations
if ! alembic -c alembic_master.ini upgrade head 2>&1 | tee alembic_master.log; then
    echo "❌ Master migrations failed!"
    cat alembic_master.log
    exit 1
fi

echo "✅ Migrations completed successfully."
echo "Starting application on port $PORT..."
exec gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
