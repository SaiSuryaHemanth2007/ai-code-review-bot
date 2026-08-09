# Use the official Python runtime

FROM python:3.12-slim

# Prevent Python from creating .pyc files

ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is sent straight to the terminal

ENV PYTHONUNBUFFERED=1

# Set working directory

WORKDIR /app

# Create a non-root application user

RUN useradd --create-home --shell /usr/sbin/nologin appuser

# Create directory required by the application

RUN mkdir -p /app/backend/data && chown -R appuser:appuser /app

# Copy dependency list

COPY requirements.txt .

# Install dependencies

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source with correct ownership

COPY --chown=appuser:appuser . .

# Run application as non-root user

USER appuser

# Expose FastAPI port

EXPOSE 8000

# Container health check

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=3)" || exit 1

# Start FastAPI

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]