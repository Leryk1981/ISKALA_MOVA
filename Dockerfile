# ISKALA MOVA - Production Ready Container with Layered Architecture
FROM python:3.11-slim

# Build arguments for flexibility
ARG ENVIRONMENT=production
ARG APP_VERSION=1.1.0

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=${ENVIRONMENT}
ENV APP_VERSION=${APP_VERSION}

# Labels for container metadata
LABEL maintainer="ISKALA Team"
LABEL version="${APP_VERSION}"
LABEL description="ISKALA MOVA - Layered Architecture with FastAPI"
LABEL environment="${ENVIRONMENT}"

# System dependencies with security updates
RUN apt-get update && apt-get install -y \
    git curl wget nano vim sudo \
    build-essential \
    libpq-dev \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app && \
    usermod -aG sudo app && \
    echo "app ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /app

# Copy dependency files first for better caching
COPY requirements.txt requirements.stage1.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements.stage1.txt

# Additional production dependencies
RUN pip install --no-cache-dir \
    fastapi[all] \
    uvicorn[standard] \
    gunicorn \
    neo4j \
    redis \
    prometheus-client \
    structlog

# Copy layered architecture components
COPY iskala_basis/ ./iskala_basis/
COPY app.py ./
COPY tests/ ./tests/

# Copy legacy modules (for backward compatibility)
COPY src/ ./src/
COPY data/ ./data/
COPY state/ ./state/
COPY trees/ ./trees/
COPY vault/ ./vault/
COPY rag_system/ ./rag_system/
COPY shield/ ./shield/
COPY translation/ ./translation/
COPY tool_api/ ./tool_api/
COPY universal_api_connector/ ./universal_api_connector/

# Copy OpenAPI Tool Server (legacy)
COPY iskala_openapi_server.py ./

# Copy documentation
COPY STAGE_1_*.md ./docs/
COPY README.md ./

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/workspace \
    /app/state/logs \
    /app/vector_db \
    /app/adapters \
    /app/data/capsules \
    /app/logs \
    /app/monitoring \
    /app/config && \
    chown -R app:app /app && \
    chmod -R 755 /app

# Switch to non-root user
USER app

# Health check for the new FastAPI application
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 8080 9090

# Default command - run the new FastAPI application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 