#!/bin/sh
set -e

cd /workspace/backend
python manage.py migrate --noinput
python manage.py ensure_budget_data

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-1}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"