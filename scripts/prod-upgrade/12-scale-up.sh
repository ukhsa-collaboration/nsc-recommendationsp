#!/usr/bin/env bash
# Step 12 of the prod PG 12->16 upgrade runbook.
# Scale django-webpack, celery-worker, celery-beat back to their original replica counts.
# See docs/runbooks/prod-pg-upgrade.md section "12 - Scale back up".
#
# Usage: scripts/prod-upgrade/12-scale-up.sh <namespace>
#
# Requires: oc logged in, edit access.
# Prereqs:  11-verify-pg16.sh exited 0.
# Outputs:  app serving traffic on PG 16.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
