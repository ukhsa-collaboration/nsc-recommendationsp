#!/usr/bin/env bash
# Step 02 of the prod PG 12->15 upgrade runbook.
# Poll pg_stat_activity until no active non-idle connections remain.
# See docs/runbooks/prod-pg-upgrade.md section "02 - Wait for DB to quiesce".
#
# Usage: scripts/prod-upgrade/02-wait-for-quiet.sh <namespace>
#
# Requires: oc logged in, edit access (exec into postgresql pod).
# Prereqs:  01-scale-down.sh completed.
# Outputs:  exit 0 once DB is quiet; exit non-zero if still busy after timeout.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
