#!/usr/bin/env bash
# Step 09 of the prod PG 12->15 upgrade runbook.
# Verify the PG 15 upgrade. Same shape as step 07 but at the final target version.
# See docs/runbooks/prod-pg-upgrade.md section "09 - Verify PG 15".
#
# Usage: scripts/prod-upgrade/09-verify-pg15.sh <namespace>
#
# Requires: oc logged in, edit access (exec into pod).
# Prereqs:  08-upgrade-13-to-15.sh completed.
# Outputs:  exit 0 if PG 15 looks healthy; exit non-zero with diagnostic if not.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
