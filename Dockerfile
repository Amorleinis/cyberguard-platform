# Docker Configuration for CyberGuard Enterprise Platform
# Production-ready multi-stage build

# Stage 1: Base image with Python
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 cyberguard && \
    mkdir -p /app /app/data /app/logs && \
    chown -R cyberguard:cyberguard /app

WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install optional dependencies for enterprise features
RUN pip install --no-cache-dir \
    scikit-learn>=1.3.0 \
    numpy>=1.24.0 \
    reportlab>=4.0.0 \
    redis>=5.0.0 \
    psycopg2-binary>=2.9.0

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY --chown=cyberguard:cyberguard . .

# Create necessary directories
RUN mkdir -p \
    data/cache \
    data/config \
    data/logs \
    data/ml_models \
    data/reports \
    data/quarantine \
    && chown -R cyberguard:cyberguard data

# Switch to app user
USER cyberguard

# Expose ports
EXPOSE 5000 8000 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command (can be overridden)
CMD ["python", "scripts/threat_dashboard.py"]

# Stage 4: Production (minimal image)
FROM python:3.11-slim as production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 cyberguard && \
    mkdir -p /app /app/data /app/logs && \
    chown -R cyberguard:cyberguard /app

WORKDIR /app

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application from application stage
COPY --from=application --chown=cyberguard:cyberguard /app .

USER cyberguard

EXPOSE 5000 8000 9000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "scripts/threat_dashboard.py"]
