#!/bin/sh
set -e

echo "Running database migrations..."
alembic -c /app/backend/alembic.ini upgrade head

echo "Starting CORTANA API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
