FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY __init__.py .
COPY app ./app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application with gunicorn in production
CMD ["sh", "-c", "if [ \"$ENV\" = 'development' ]; then python run.py; else exec gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000} main:app --workers ${WORKERS:-2} --timeout 60; fi"]