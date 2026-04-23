#!/usr/bin/env bash
# Step 05 of the prod PG 12->15 upgrade runbook.
# Take an ODF Ceph RBD VolumeSnapshot of the postgresql PVC. Belt-and-braces alongside the S3 dump.
# See docs/runbooks/prod-pg-upgrade.md section "05 - PV snapshot".
#
# Usage: scripts/prod-upgrade/05-snapshot-pv.sh <namespace>
#
# Requires: oc logged in, VolumeSnapshot verb in the namespace (unverified - check on Fri).
# Prereqs:  04-restore-drill.sh succeeded.
# Outputs:  a VolumeSnapshot resource in the namespace, ready as a quick rollback target.
#
# FALLBACK: if VolumeSnapshot RBAC isn't available, document that in the runbook and
# rely on the step-03 S3 dump + step-04 restore-drill as the sole safety net.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
