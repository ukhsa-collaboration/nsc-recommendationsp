#!/usr/bin/env bash
# Step 00 of the prod PG 12->15 upgrade runbook.
# Preflight: verify cluster, branch, and image are in the expected state before starting.
# See docs/runbooks/prod-pg-upgrade.md section "00 - Preflight".
#
# Usage: scripts/prod-upgrade/00-preflight.sh <namespace>
#
# Requires: oc logged in, view access in the namespace.
# Prereqs:  none (this is the first step).
# Outputs:  exit 0 if safe to proceed; exit non-zero with diagnostic if not.

set -euo pipefail

echo "TODO: implement this step" >&2
exit 1
