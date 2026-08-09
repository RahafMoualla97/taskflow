FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including netcat for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose the application port
EXPOSE 8000

# Set the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]