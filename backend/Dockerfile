FROM python:3.11-slim

WORKDIR /app

# تثبيت dependencies النظام (مع إضافة netcat-openbsd)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملفات المتطلبات
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# إعطاء صلاحية التنفيذ لـ entrypoint
RUN chmod +x entrypoint.sh

# منفذ التشغيل
EXPOSE 8000

# نقطة الدخول
ENTRYPOINT ["./entrypoint.sh"]