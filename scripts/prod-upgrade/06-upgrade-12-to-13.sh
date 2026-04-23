#!/usr/bin/env bash
# Step 06 of the prod PG 12->16 upgrade runbook.
# Patch the postgresql DeploymentConfig image tag 12->13. SCL image auto-upgrades
# via POSTGRESQL_UPGRADE=copy. Wait for new pod Ready.
# See docs/runbooks/prod-pg-upgrade.md section "06 - Upgrade 12 -> 13".
#
# Usage: scripts/prod-upgrade/06-upgrade-12-to-13.sh <namespace>
#
# Requires: oc logged in, edit access, DeploymentConfig patch permission.
# Prereqs:  05-snapshot-pv.sh done (or documented skip).
# Outputs:  postgresql DC at PG 13, new pod Ready, upgrade-complete line in logs.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
