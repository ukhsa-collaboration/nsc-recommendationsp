#!/usr/bin/env bash
# Step 04 of the prod PG 12->16 upgrade runbook.
# Restore drill: prove the latest dump in the bucket is actually restorable.
# Spins up a throwaway PG 15 pod from the postgresql-backup image, fetches
# the latest .dump via restore_helper.py, pg_restore's it, runs restore_verify.py
# against the restored state, then drops the pod.
# See docs/runbooks/prod-pg-upgrade.md section "04 - Restore drill".
#
# Usage: scripts/prod-upgrade/04-restore-drill.sh [namespace] [--target throwaway|dev]
#   namespace defaults to uknscr-development; uknscr-production prompts for yes.
#   --target throwaway (default): ephemeral pod in the same namespace, pod is
#       deleted on exit. PG major version is 15 regardless of source -- this
#       proves the dump is recoverable, not that it restores into the source
#       major version. For rollback assurance we rely on POSTGRESQL_UPGRADE=copy
#       keeping the original PG 12 data dir in place beside the new one.
#   --target dev (one-shot integration test): restores the namespace's latest
#       dump into uknscr-development. NOT implemented yet -- used only for the
#       chunk 2 dev-playground setup, handled ad-hoc there.

set -euo pipefail

# Git Bash on Windows otherwise rewrites Unix paths in args to oc.exe
# (e.g. /var/lib/pgsql/data -> C:/Program Files/Git/var/lib/pgsql/data),
# breaking remote-pod commands. No effect on Mac/Linux.
export MSYS_NO_PATHCONV=1

NAMESPACE="uknscr-development"
TARGET="throwaway"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --target) TARGET="$2"; shift 2 ;;
        -*) echo "unknown flag: $1" >&2; exit 2 ;;
        *) NAMESPACE="$1"; shift ;;
    esac
done

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Restore drill against PRODUCTION (throwaway pod only). Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

if [[ "$TARGET" != "throwaway" ]]; then
    echo "FAIL: target '$TARGET' not yet implemented (only 'throwaway' is supported)" >&2
    exit 2
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

IMAGE="image-registry.openshift-image-registry.svc:5000/uknscr-build/postgresql-backup:latest"
DRILL_POD="pg-restore-drill-$$"

AWS_KEY=$(oc get secret backups -n "$NAMESPACE" -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d)
AWS_SECRET=$(oc get secret backups -n "$NAMESPACE" -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 -d)
BUCKET=$(oc get configmap backups -n "$NAMESPACE" -o jsonpath='{.data.BUCKET_NAME}')
[[ -n "$AWS_KEY" && -n "$AWS_SECRET" && -n "$BUCKET" ]] \
    || fail "could not read backup credentials from secret/configmap 'backups' in $NAMESPACE"

echo "== Restore drill: $NAMESPACE (target=$TARGET) =="
echo "drill pod:        $DRILL_POD"
echo "source bucket:    $BUCKET"

cleanup() {
    echo "cleaning up drill pod $DRILL_POD" >&2
    oc delete pod "$DRILL_POD" -n "$NAMESPACE" --wait=false --ignore-not-found 2>/dev/null || true
}
trap cleanup EXIT

# Note: do NOT set PGUSER/PGDATABASE at the pod level -- SCL's run-postgresql
# reads those during bootstrap and tries to authenticate as them before the
# role exists. Only POSTGRESQL_* for init; PG* come in per-exec below.
oc run "$DRILL_POD" -n "$NAMESPACE" \
    --image="$IMAGE" \
    --restart=Never \
    --env="POSTGRESQL_USER=drill" \
    --env="POSTGRESQL_PASSWORD=drillpass" \
    --env="POSTGRESQL_DATABASE=drill" \
    --env="AWS_ACCESS_KEY_ID=$AWS_KEY" \
    --env="AWS_SECRET_ACCESS_KEY=$AWS_SECRET" \
    --env="BUCKET_NAME=$BUCKET" \
    --command -- /usr/bin/run-postgresql >/dev/null

echo "waiting for drill PG to be Ready..."
oc wait --for=condition=Ready "pod/$DRILL_POD" -n "$NAMESPACE" --timeout=3m \
    || { oc logs -n "$NAMESPACE" "$DRILL_POD" --tail=30 >&2; fail "drill pod never became Ready"; }

# SCL flips Ready when postgres accepts connections, but the init script may
# still be finalising (createuser/createdb run after the socket opens).
sleep 3

EXEC_ENV=(env PGUSER=drill PGPASSWORD=drillpass PGDATABASE=drill PGHOST=localhost)

echo "fetching + restoring latest dump..."
oc exec -n "$NAMESPACE" "$DRILL_POD" -- "${EXEC_ENV[@]}" \
    python3 /usr/local/bin/restore_helper.py \
    || fail "restore_helper failed"

STAMP=$(date -u +%Y%m%d-%H%M%S)
VERIFY_OUT="/tmp/restore-drill-${NAMESPACE}-${STAMP}.txt"
echo "verifying restored state..."
oc exec -n "$NAMESPACE" "$DRILL_POD" -- "${EXEC_ENV[@]}" \
    python3 /usr/local/bin/restore_verify.py \
    > "$VERIFY_OUT" \
    || fail "restore_verify failed"

echo "verify output:    $VERIFY_OUT"
echo "drill pg version: $(grep '^pg_version=' "$VERIFY_OUT" | cut -d= -f2)"
echo "drill schema hash: $(grep -oE '[0-9a-f]{64}' "$VERIFY_OUT" | head -1)"
echo "OK"
