#!/usr/bin/env bash
# Step 00 of the prod PG 12->16 upgrade runbook.
# Preflight: read the current state of the target namespace and snapshot
# row counts + schema hash so later verify steps have a baseline to diff against.
# See docs/runbooks/prod-pg-upgrade.md section "00 - Preflight".
#
# Usage: scripts/prod-upgrade/00-preflight.sh [namespace]
#   namespace defaults to uknscr-development. uknscr-production prompts for yes.
#
# Outputs: writes /tmp/uknscr-preflight-<ns>-<timestamp>.txt with a row-count
# snapshot + schema hash for 07-verify-pg13.sh / 09-verify-pg15.sh to read.

set -euo pipefail

# Git Bash on Windows otherwise rewrites Unix paths in args to oc.exe
# (e.g. /var/lib/pgsql/data -> C:/Program Files/Git/var/lib/pgsql/data),
# breaking remote-pod commands. No effect on Mac/Linux.
export MSYS_NO_PATHCONV=1

NAMESPACE="${1:-uknscr-development}"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Preflight against PRODUCTION. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

echo "== Preflight: $NAMESPACE =="

oc get ns "$NAMESPACE" >/dev/null 2>&1 || fail "namespace $NAMESPACE not accessible"

POD=$(oc get pod -n "$NAMESPACE" -l deploymentconfig=postgresql \
    -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | awk '{print $1}')
[[ -n "$POD" ]] || fail "no Running postgresql pod in $NAMESPACE"

IMAGE=$(oc get dc postgresql -n "$NAMESPACE" \
    -o jsonpath='{.spec.template.spec.containers[0].image}')
TRIGGER_COUNT=$(oc get dc postgresql -n "$NAMESPACE" \
    -o jsonpath='{.spec.triggers[?(@.type=="ImageChange")].type}' | wc -w | tr -d ' ')

DBSIZE=$(oc exec -n "$NAMESPACE" "$POD" -- bash -c \
    'psql -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -tAc \
    "SELECT pg_size_pretty(pg_database_size(current_database()));"' 2>/dev/null) \
    || fail "psql connection failed inside pod $POD"

PVC_LINE=$(oc exec -n "$NAMESPACE" "$POD" -- df -hP /var/lib/pgsql/data | tail -1)
PVC_USED_PCT=$(echo "$PVC_LINE" | awk '{sub("%","",$5); print $5}')
PVC_AVAIL=$(echo "$PVC_LINE" | awk '{print $4}')
(( PVC_USED_PCT < 50 )) || fail "PVC is ${PVC_USED_PCT}% full; upgrade=copy needs ~2x current DB size free"

# Snapshot row counts + schema hash for later verify diffs. We run
# restore_verify.py via a side pod so the baseline format (exact COUNT(*))
# matches what 07/09/11 emit. n_live_tup from pg_stat_user_tables would be
# both stale (autovacuum-driven) on the source and zero post-pg_upgrade,
# making cross-hop diffs meaningless.
PGUSER=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-user}' | base64 -d)
PGPASSWORD=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-password}' | base64 -d)
PGDATABASE=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-name}' | base64 -d)
[[ -n "$PGUSER" && -n "$PGPASSWORD" && -n "$PGDATABASE" ]] \
    || fail "could not read postgresql secret in $NAMESPACE"

VERIFY_IMAGE="image-registry.openshift-image-registry.svc:5000/uknscr-build/postgresql-backup:latest"

STAMP=$(date -u +%Y%m%d-%H%M%S)
SNAPSHOT="/tmp/uknscr-preflight-${NAMESPACE}-${STAMP}.txt"
VERIFY_OUT=$(mktemp)
trap 'rm -f "$VERIFY_OUT"' EXIT

oc run "preflight-${STAMP}" -n "$NAMESPACE" \
    --rm -i --restart=Never --quiet \
    --image="$VERIFY_IMAGE" \
    --env="PGHOST=postgresql" \
    --env="PGUSER=$PGUSER" \
    --env="PGPASSWORD=$PGPASSWORD" \
    --env="PGDATABASE=$PGDATABASE" \
    --command -- python3 /usr/local/bin/restore_verify.py \
    > "$VERIFY_OUT" 2>&1 \
    || { cat "$VERIFY_OUT" >&2; fail "restore_verify failed"; }

PGVERSION=$(grep '^pg_version=' "$VERIFY_OUT" | cut -d= -f2)
[[ -n "$PGVERSION" ]] || { cat "$VERIFY_OUT" >&2; fail "could not parse pg_version from restore_verify output"; }

{
    echo "# preflight snapshot"
    echo "namespace=$NAMESPACE"
    echo "timestamp=$STAMP"
    echo "pod=$POD"
    echo "image=$IMAGE"
    echo "dc_trigger_count=$TRIGGER_COUNT"
    echo "db_size=$DBSIZE"
    echo "pvc_used_pct=$PVC_USED_PCT"
    echo "pvc_avail=$PVC_AVAIL"
    echo ""
    cat "$VERIFY_OUT"
} > "$SNAPSHOT"

echo "pod:              $POD"
echo "image:            $IMAGE"
echo "pg version:       $PGVERSION"
echo "db size:          $DBSIZE"
echo "pvc usage:        ${PVC_USED_PCT}% used, $PVC_AVAIL free"
echo "dc img triggers:  $TRIGGER_COUNT  (upgrade scripts will replace these with a single target-version trigger)"
echo "snapshot:         $SNAPSHOT"

# Check backup freshness (best-effort; warn only)
LAST_BACKUP=$(oc get cronjob postgresql-backup -n "$NAMESPACE" \
    -o jsonpath='{.status.lastSuccessfulTime}' 2>/dev/null || echo "")
if [[ -n "$LAST_BACKUP" ]]; then
    echo "last backup:      $LAST_BACKUP"
else
    echo "last backup:      UNKNOWN (no postgresql-backup cronjob or no successful runs yet)" >&2
fi

echo "OK"
