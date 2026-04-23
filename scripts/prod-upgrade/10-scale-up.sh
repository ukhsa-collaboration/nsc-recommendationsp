#!/usr/bin/env bash
# Step 10 of the prod PG 12->15 upgrade runbook.
# Scale django-webpack, celery-worker, celery-beat back to their original replica counts.
# Flip the maintenance page off (if there is one).
# See docs/runbooks/prod-pg-upgrade.md section "10 - Scale back up".
#
# Usage: scripts/prod-upgrade/10-scale-up.sh <namespace>
#
# Requires: oc logged in, edit access.
# Prereqs:  09-verify-pg15.sh exited 0.
# Outputs:  app serving traffic on PG 15.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
