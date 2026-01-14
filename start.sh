#!/bin/bash
# Startup script for Render - runs migrations and starts gunicorn

set -e

echo "Running database migrations..."
python manage.py migrate --noinput 2>/dev/null || {
    echo "  Migrations skipped (database may not be ready yet)"
}

echo "Starting Gunicorn..."
exec gunicorn A2SVTracker.wsgi:application --bind 0.0.0.0:$PORT
