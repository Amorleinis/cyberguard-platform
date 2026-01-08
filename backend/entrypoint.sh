#!/bin/sh
set -e

APP_HOST=${APP_HOST:-0.0.0.0}
APP_PORT=${APP_PORT:-8000}
APP_MODULE=${APP_MODULE:-app.main:app}

run_migrations() {
  attempts=0
  max_attempts=${ALEMBIC_MAX_ATTEMPTS:-5}
  sleep_secs=${ALEMBIC_SLEEP_SECS:-3}

  if [ "${DATABASE_URL#sqlite}" != "${DATABASE_URL}" ]; then
    # Skip retries for sqlite; no network wait needed
    alembic upgrade head && return 0
  fi

  until alembic upgrade head; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge "$max_attempts" ]; then
      echo "Alembic upgrade failed after ${attempts} attempts" >&2
      return 1
    fi
    echo "Alembic upgrade failed (attempt ${attempts}/${max_attempts}); retrying in ${sleep_secs}s..."
    sleep "$sleep_secs"
  done
}

run_migrations

exec python -m uvicorn "$APP_MODULE" --host "$APP_HOST" --port "$APP_PORT"
