#!/bin/sh

set -e

echo "Waiting for startup..."

echo "Applying migrations..."
alembic upgrade head

echo "Filling database..."

python tools/fill_db_base_users_data.py || true
python tools/fill_db_payment_data.py || true
python tools/fill_db_production_calendar.py || true
python tools/fill_db_staff_data.py || true

echo "Creating Mongo collections..."

python tools/create_mongo_db_collections.py || true

echo "Starting Gunicorn..."

exec gunicorn \
    --bind 0.0.0.0:8000 \
    --timeout 200 \
    wsgi:app