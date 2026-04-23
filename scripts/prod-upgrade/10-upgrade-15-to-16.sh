#!/usr/bin/env bash
# Step 10 of the prod PG 12->16 upgrade runbook.
# Third hop: patch DeploymentConfig image tag 15->16. Same pattern as step 06.
# See docs/runbooks/prod-pg-upgrade.md section "10 - Upgrade 15 -> 16".
#
# Usage: scripts/prod-upgrade/10-upgrade-15-to-16.sh <namespace>
#
# Requires: oc logged in, edit access, DeploymentConfig patch permission.
# Prereqs:  09-verify-pg15.sh exited 0.
# Outputs:  postgresql DC at PG 16, new pod Ready, upgrade-complete line in logs.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
