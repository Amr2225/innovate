# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=main.settings \
    DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS:-"localhost 127.0.0.1 [::1] *"} \
    DEBUG=${DEBUG:-False} \
    SECRET_KEY=${SECRET_KEY} \
    SQL_ENGINE=${SQL_ENGINE} \
    SQL_DATABASE=${SQL_DATABASE} \
    SQL_USER=${SQL_USER} \
    SQL_PASSWORD=${SQL_PASSWORD} \
    SQL_HOST=${SQL_HOST} \
    SQL_PORT=${SQL_PORT} \
    EMAIL_HOST_USER=${EMAIL_HOST_USER} \
    EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD} \
    PAYMOB_PK=${PAYMOB_PK} \
    PAYMOB_SK=${PAYMOB_SK} \
    CLIENT_URL=${CLIENT_URL} \
    AI_API_KEY=${AI_API_KEY} \
    AI_PROVIDER=${AI_PROVIDER} \
    AI_MODEL=${AI_MODEL}

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for static files
RUN mkdir -p /app/static

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:8000"]
