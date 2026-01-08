FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ALEMBIC_CONFIG=/app/backend/alembic.ini

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Entrypoint
COPY entrypoint.sh /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh

# Non-root user
RUN useradd -m -u 1000 backend && chown -R backend:backend /app
USER backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["/app/backend/entrypoint.sh"]
