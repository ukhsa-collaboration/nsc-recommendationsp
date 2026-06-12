#!/usr/bin/env bash
# Run Django management commands with all required environment variables.
# Usage: ./scripts/manage.sh <command> [args...]
#
# Examples:
#   ./scripts/manage.sh makemigrations --check --dry-run
#   ./scripts/manage.sh migrate
#   ./scripts/manage.sh clear_cache

set -euo pipefail

export DJANGO_CONFIGURATION=Test
export DATABASE_ENGINE=postgresql
export DATABASE_NAME=test
export DATABASE_HOST=localhost
export DATABASE_USER=nsc
export DATABASE_PASSWORD=nsc
export REDIS_SERVICE_HOST=localhost
export DJANGO_ADMIN_IP_RANGES="127.0.0.1/32"

exec .venv/bin/python manage.py "$@"
