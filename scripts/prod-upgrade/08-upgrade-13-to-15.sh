#!/usr/bin/env bash
# Step 08 of the prod PG 12->15 upgrade runbook.
# Second hop: patch DeploymentConfig image tag 13->15. Same pattern as step 06.
# See docs/runbooks/prod-pg-upgrade.md section "08 - Upgrade 13 -> 15".
#
# Usage: scripts/prod-upgrade/08-upgrade-13-to-15.sh <namespace>
#
# Requires: oc logged in, edit access, DeploymentConfig patch permission.
# Prereqs:  07-verify-pg13.sh exited 0.
# Outputs:  postgresql DC at PG 15, new pod Ready, upgrade-complete line in logs.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
