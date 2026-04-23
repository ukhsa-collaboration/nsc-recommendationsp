#!/usr/bin/env bash
# Step 11 of the prod PG 12->16 upgrade runbook.
# Verify the PG 16 upgrade. Same shape as step 07 but at the final target version.
# See docs/runbooks/prod-pg-upgrade.md section "11 - Verify PG 16".
#
# Usage: scripts/prod-upgrade/11-verify-pg16.sh <namespace>
#
# Requires: oc logged in, edit access (exec into pod).
# Prereqs:  10-upgrade-15-to-16.sh completed.
# Outputs:  exit 0 if PG 16 looks healthy; exit non-zero with diagnostic if not.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
