#!/usr/bin/env bash
# Step 01 of the prod PG 12->16 upgrade runbook.
# Scale down celery-beat, celery-worker, and django-webpack so the DB goes quiet.
# See docs/runbooks/prod-pg-upgrade.md section "01 - Scale down workers".
#
# Usage: scripts/prod-upgrade/01-scale-down.sh <namespace>
#
# Requires: oc logged in, edit access (uknscr-editors) in the namespace.
# Prereqs:  00-preflight.sh exited 0.
# Outputs:  celery and webpack deployments scaled to 0; replica counts recorded for 10-scale-up.sh.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
