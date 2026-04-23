#!/usr/bin/env bash
# Step 12 of the prod PG 12->16 upgrade runbook.
# Restore app DC replica counts from the snapshot written by 01-scale-down.sh.
# See docs/runbooks/prod-pg-upgrade.md section "12 - Scale back up".
#
# Usage: scripts/prod-upgrade/12-scale-up.sh [namespace]
#   namespace defaults to uknscr-development; uknscr-production prompts for yes.

set -euo pipefail

NAMESPACE="${1:-uknscr-development}"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Scale up workloads in PRODUCTION. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

SCALES="/tmp/uknscr-scales-${NAMESPACE}-latest.env"
[[ -e "$SCALES" ]] || fail "no scale snapshot at $SCALES -- did 01-scale-down.sh run?"

echo "== Scale up: $NAMESPACE =="
echo "restoring from $(readlink -f "$SCALES" 2>/dev/null || echo "$SCALES")"

DCS=()
while IFS='=' read -r dc n; do
    [[ -z "$dc" ]] && continue
    echo "  $dc: 0 -> $n"
    oc scale dc "$dc" --replicas="$n" -n "$NAMESPACE" >/dev/null
    DCS+=("$dc")
done < "$SCALES"

echo "waiting for rollouts to complete..."
for dc in "${DCS[@]}"; do
    oc rollout status dc "$dc" -n "$NAMESPACE" --timeout=5m \
        || fail "rollout of $dc did not complete"
done

echo "all app DCs restored and Ready"
echo "OK"
