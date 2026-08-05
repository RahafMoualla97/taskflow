#!/bin/bash

echo "🚀 Starting TaskFlow Backend..."

# انتظار حتى تكون قاعدة البيانات جاهزة
echo "⏳ Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ Database is ready!"

# تشغيل الهجرات (migrations)
echo "📦 Running database migrations..."
alembic upgrade head

# تشغيل السيرفر
echo "🔥 Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000