#!/usr/bin/env bash
# Step 07 of the prod PG 12->16 upgrade runbook.
# Verify the PG 13 upgrade: row counts match pre-upgrade, connection check, log grep for
# the pg_upgrade-complete line.
# See docs/runbooks/prod-pg-upgrade.md section "07 - Verify PG 13".
#
# Usage: scripts/prod-upgrade/07-verify-pg13.sh <namespace>
#
# Requires: oc logged in, edit access (exec into pod).
# Prereqs:  06-upgrade-12-to-13.sh completed.
# Outputs:  exit 0 if PG 13 looks healthy; exit non-zero with diagnostic if not.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
