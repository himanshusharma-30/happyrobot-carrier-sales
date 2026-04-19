# syntax=docker/dockerfile:1

# Use slim Python for small image size
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install system deps (curl for healthcheck; keep layer small)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (separate layer → faster rebuilds when only code changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY loads.json .

# Non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose the app port
EXPOSE 8000

# Healthcheck - Docker/Cloud Run/etc can hit this to know the container is alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the API with uvicorn (no --reload in prod)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]