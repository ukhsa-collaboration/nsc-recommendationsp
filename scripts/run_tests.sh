#!/usr/bin/env bash
# Run the Django test suite with all required environment variables.
# Usage: ./scripts/run_tests.sh [pytest args...]
#
# Examples:
#   ./scripts/run_tests.sh                        # full suite
#   ./scripts/run_tests.sh nsc/policy/tests/ -v   # single app
#   ./scripts/run_tests.sh -k test_name           # single test

set -euo pipefail

export DJANGO_CONFIGURATION=Test
export DATABASE_ENGINE=postgresql
export DATABASE_NAME=test
export DATABASE_HOST=localhost
export DATABASE_USER=nsc
export DATABASE_PASSWORD=nsc
export REDIS_SERVICE_HOST=localhost
export DJANGO_ADMIN_IP_RANGES="127.0.0.1/32"

exec .venv/bin/pytest "$@"
