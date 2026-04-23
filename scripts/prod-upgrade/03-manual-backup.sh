#!/usr/bin/env bash
# Step 03 of the prod PG 12->16 upgrade runbook.
# Trigger a manual backup NOW (fresh, known-quiet dump). Not relying on the 02:30 UTC daily run.
# See docs/runbooks/prod-pg-upgrade.md section "03 - Take pre-upgrade backup".
#
# Usage: scripts/prod-upgrade/03-manual-backup.sh <namespace>
#
# Requires: oc logged in, edit access. `postgresql-backup` CronJob exists in the namespace.
# Prereqs:  02-wait-for-quiet.sh exited 0.
# Outputs:  one new object in s3://<backups-bucket>/uknscr-<ts>.dump with verified PGDMP magic.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
