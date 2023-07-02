#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Copy static files
echo "Copy static files"
cp -r /app/backend_static/. /backend_static/static/

# Apply database migrations
echo "Apply migrations"
python manage.py migrate

# Start gunicorn server
echo "Start server"
gunicorn --bind 0.0.0.0:8000 backend.wsgi