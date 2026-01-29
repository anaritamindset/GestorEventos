# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories in /tmp (writable filesystem)
RUN mkdir -p /tmp/uploads /tmp/certificados

# Set environment variables
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run the application using gunicorn
CMD exec gunicorn --bind :8080 --workers 2 --threads 4 --timeout 0 main:app
