#!/bin/bash

echo "Starting TaskFlow Backend..."

echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000