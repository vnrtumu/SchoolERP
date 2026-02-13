#!/bin/sh
set -e
echo "Running migrations..."
alembic upgrade head
alembic -c alembic_master.ini upgrade head
echo "Starting application..."
exec gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
