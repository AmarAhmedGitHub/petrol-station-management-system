# Petrol Station Management System - Production Dockerfile

FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app \
    && chown -R app:app /app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY deploy/requirements-production.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-production.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs backups \
    && chown -R app:app logs backups

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import streamlit; print('Streamlit available')" || exit 1

# Expose port
EXPOSE 8501

# Start application
CMD ["streamlit", "run", "main_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
