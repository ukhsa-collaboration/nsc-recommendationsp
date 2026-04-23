#!/usr/bin/env bash
# Step 01 of the prod PG 12->16 upgrade runbook.
# Scale down celery-beat, celery-worker, and django-webpack so the DB goes quiet.
# Records prior replica counts to /tmp/uknscr-scales-<ns>-<stamp>.env so
# 12-scale-up.sh can restore them exactly.
# See docs/runbooks/prod-pg-upgrade.md section "01 - Scale down workers".
#
# Usage: scripts/prod-upgrade/01-scale-down.sh [namespace]
#   namespace defaults to uknscr-development; uknscr-production prompts for yes.

set -euo pipefail

NAMESPACE="${1:-uknscr-development}"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Scale down workloads in PRODUCTION. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

DCS=(django-webpack django-webpack-celery-beat django-webpack-celery-worker)

STAMP=$(date -u +%Y%m%d-%H%M%S)
SCALES="/tmp/uknscr-scales-${NAMESPACE}-${STAMP}.env"

echo "== Scale down: $NAMESPACE =="
echo "recording replica counts to $SCALES"
: > "$SCALES"

for dc in "${DCS[@]}"; do
    oc get dc "$dc" -n "$NAMESPACE" >/dev/null 2>&1 \
        || fail "DC $dc not found in $NAMESPACE"
    n=$(oc get dc "$dc" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
    echo "${dc}=${n}" >> "$SCALES"
    echo "  $dc: $n -> 0"
done

# Also expose the most recent scales file via a stable symlink so 12-scale-up
# can find it without being told the timestamp.
ln -sf "$SCALES" "/tmp/uknscr-scales-${NAMESPACE}-latest.env"

for dc in "${DCS[@]}"; do
    oc scale dc "$dc" --replicas=0 -n "$NAMESPACE" >/dev/null
done

echo "waiting for pods to terminate..."
for dc in "${DCS[@]}"; do
    oc wait --for=delete pod -n "$NAMESPACE" -l "deploymentconfig=$dc" --timeout=2m \
        2>/dev/null || true
done

# Confirm all the app pods are gone (postgresql pod may remain)
remaining=$(oc get pod -n "$NAMESPACE" --no-headers \
    -l 'deploymentconfig in (django-webpack,django-webpack-celery-beat,django-webpack-celery-worker)' \
    2>/dev/null | wc -l | tr -d ' ')
(( remaining == 0 )) || fail "$remaining app pod(s) still running after scale-down"

echo "all app DCs scaled to 0"
echo "scale snapshot:   $SCALES"
echo "OK"
