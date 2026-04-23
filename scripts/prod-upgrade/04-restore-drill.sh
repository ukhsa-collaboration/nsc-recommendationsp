#!/usr/bin/env bash
# Step 04 of the prod PG 12->15 upgrade runbook.
# Restore the just-taken dump into a scratch namespace + ephemeral PG pod. Prove the backup is usable.
# See docs/runbooks/prod-pg-upgrade.md section "04 - Restore drill".
#
# Usage: scripts/prod-upgrade/04-restore-drill.sh <namespace>
#
# Requires: oc logged in, cluster-level permission to create a scratch namespace,
#           or a pre-provisioned scratch namespace the runner can use.
# Prereqs:  03-manual-backup.sh completed with a verified dump in the bucket.
# Outputs:  scratch ns created, dump restored into fresh PG 12 pod, verification queries logged,
#           scratch ns torn down.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
