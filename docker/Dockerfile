FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for better caching
COPY pyproject.toml .

# Copy source code
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Copy data files
COPY data/ ./data/

# Create directories for mounted volumes
RUN mkdir -p /root/.cache/wal

# Set environment variables
ENV HOMEPAGE_HOST=0.0.0.0 \
    HOMEPAGE_PORT=5000 \
    HOMEPAGE_ENV=production \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run application
CMD ["python", "-m", "homepage.app"]
