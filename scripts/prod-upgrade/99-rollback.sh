#!/usr/bin/env bash
# Step 99 of the prod PG 12->16 upgrade runbook. NOT a numbered step in the happy path.
# Runbook-guided rollback. Invoked manually by the runner if something goes sideways.
# See docs/runbooks/prod-pg-upgrade.md section "Rollback".
#
# Usage: scripts/prod-upgrade/99-rollback.sh <namespace>
#
# Requires: oc logged in, edit access. Specific extras depend on rollback path (see runbook):
#   - Plan A: VolumeSnapshot restore (if step 05 succeeded)
#   - Plan B: fresh PV + restore from the step-03 S3 dump
#   - Plan C: DC image tag revert (only viable if pg_upgrade hasn't overwritten disk yet)
#
# Outputs:  best-effort return to the pre-upgrade state; runner decides which plan to execute.

set -euo pipefail

echo "TODO: implement this step - rollback is deliberately manual; populate after Fri's staging rehearsal" >&2
exit 1
