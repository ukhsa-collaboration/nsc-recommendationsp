#!/usr/bin/env bash
# Reset a uknscr namespace's postgresql DC back to PG 12 with fresh data
# loaded from the most recent PG 12 dump in the backup bucket.
#
# Used AFTER a prod-upgrade dress rehearsal against staging to hand
# staging back in a pre-upgrade state, so an L2 engineer can run their
# own independent rehearsal before the real prod window.
#
# HARD REFUSES to run against uknscr-production. Destroys the current
# postgresql PVC unconditionally; the bucket dump is the only source of
# truth for the restored data.
#
# Usage: scripts/ops/reset-to-pg12.sh <namespace> [--dump-key KEY]
#   namespace: uknscr-staging or uknscr-development.
#   --dump-key: specific uknscr-*.dump key in the backups bucket; must
#               be a PG 12 dump. Default: pick most recent dump with a
#               2026-04-23 or earlier timestamp (assumed pre-upgrade).
#
# Procedure (matches what we did in Phase 1.5 for dev today):
#   1. Scale app DCs (django-webpack + celery-{beat,worker}) to 0.
#   2. Scale postgresql DC to 0; delete postgresql pod.
#   3. Delete the postgresql PVC (with the same "kill stale debug pods
#      first" dance that unblocks pvc-protection finalizers).
#   4. Apply a fresh empty postgresql PVC.
#   5. Strip DC ImageChange triggers down to one targeting
#      openshift/postgresql:12-el8.
#   6. Scale postgresql DC to 1; wait for Ready.
#   7. Spin a helper pod from postgresql-backup:latest that pg_restores
#      the designated dump into the fresh PG 12 DB.
#   8. Scale app DCs back to their pre-reset replica counts.
#
# This script is INTENTIONALLY destructive and INTENTIONALLY verbose.
# Read through each prompt before answering.

set -euo pipefail

# Git Bash on Windows otherwise rewrites Unix paths in args to oc.exe
# (e.g. /var/lib/pgsql/data -> C:/Program Files/Git/var/lib/pgsql/data),
# breaking remote-pod commands. No effect on Mac/Linux.
export MSYS_NO_PATHCONV=1

NAMESPACE=""
DUMP_KEY=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dump-key) DUMP_KEY="$2"; shift 2 ;;
        -*) echo "unknown flag: $1" >&2; exit 2 ;;
        *) NAMESPACE="$1"; shift ;;
    esac
done

[[ -n "$NAMESPACE" ]] || { echo "usage: $0 <namespace> [--dump-key KEY]" >&2; exit 2; }

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    echo "REFUSED: never run reset-to-pg12 against production." >&2
    exit 1
fi

read -rp "About to DESTROY the postgresql PVC in $NAMESPACE and restore from a dump. Type 'yes' to continue: " confirm
[[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }

fail() { echo "FAIL: $*" >&2; exit 1; }

echo "== Reset to PG 12: $NAMESPACE =="

# 1. Scale down app.
"$(dirname "$0")/../prod-upgrade/01-scale-down.sh" "$NAMESPACE"

# 2. Scale postgresql DC to 0 and wait for the pod.
echo "scaling postgresql DC to 0..."
oc scale dc postgresql --replicas=0 -n "$NAMESPACE" >/dev/null
oc wait --for=delete pod -n "$NAMESPACE" -l deploymentconfig=postgresql --timeout=2m 2>/dev/null || true

# 3. Delete stale debug pods that hold the PVC via pvc-protection finalizer
#    (dev hit this earlier - 41-day-old Completed pod blocked PVC deletion).
stale_debug=$(oc get pod -n "$NAMESPACE" -o name 2>/dev/null | grep -E 'postgresql-debug|-deploy$' || true)
if [[ -n "$stale_debug" ]]; then
    echo "cleaning up stale debug/deploy pods:"
    echo "$stale_debug" | sed 's/^/  /'
    echo "$stale_debug" | xargs -I {} oc delete {} -n "$NAMESPACE" --force --grace-period=0 >/dev/null 2>&1 || true
fi

echo "deleting postgresql PVC..."
oc delete pvc postgresql -n "$NAMESPACE" --wait=true --timeout=2m \
    || fail "PVC deletion did not complete (stale pod holding it open?)"

# 4. Apply a fresh empty PVC.
STORAGE=$(oc get pvc postgresql -n "$NAMESPACE" -o jsonpath='{.spec.resources.requests.storage}' 2>/dev/null || echo "10Gi")
SC=$(oc get pvc postgresql -n "$NAMESPACE" -o jsonpath='{.spec.storageClassName}' 2>/dev/null || echo "ocs-storagecluster-ceph-rbd")
# Above reads stale values (PVC still visible briefly). Safer defaults.
STORAGE="${STORAGE:-10Gi}"
SC="${SC:-ocs-storagecluster-ceph-rbd}"

echo "creating fresh PVC (${STORAGE}, $SC)..."
oc apply -n "$NAMESPACE" -f - <<EOF >/dev/null
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgresql
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: $STORAGE
  storageClassName: $SC
EOF

# 5. Strip DC triggers down to just openshift/postgresql:12-el8.
echo "normalising DC ImageChange triggers to only 12-el8..."
# Remove any known upgrade-target triggers.
for tag in \
    openshift/postgresql:13-el8 \
    postgresql:13-c9s postgresql:15-c9s postgresql:16-c9s; do
    oc set triggers dc/postgresql -n "$NAMESPACE" --remove=true \
        --from-image="$tag" -c postgresql >/dev/null 2>&1 || true
done
# Ensure 12-el8 trigger exists.
oc set triggers dc/postgresql -n "$NAMESPACE" --auto \
    --from-image=openshift/postgresql:12-el8 -c postgresql >/dev/null 2>&1 || true

# Also clear POSTGRESQL_UPGRADE in case a previous run left it set.
oc set env dc/postgresql POSTGRESQL_UPGRADE- -n "$NAMESPACE" >/dev/null 2>&1 || true

# 6. Scale DC to 1; wait for Ready.
echo "scaling postgresql DC to 1..."
oc scale dc postgresql --replicas=1 -n "$NAMESPACE" >/dev/null

echo "waiting for fresh PG 12 pod..."
for i in $(seq 1 30); do
    ready=$(oc get pod -l deploymentconfig=postgresql -n "$NAMESPACE" \
        -o jsonpath='{.items[0].status.containerStatuses[0].ready}' 2>/dev/null || echo "")
    [[ "$ready" == "true" ]] && break
    sleep 5
done
[[ "$ready" == "true" ]] || fail "new postgresql pod not Ready after 2.5m"

# 7. Restore latest (or named) PG 12 dump from the bucket via a helper pod.
PGUSER=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-user}' | base64 -d)
PGPASSWORD=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-password}' | base64 -d)
PGDATABASE=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-name}' | base64 -d)
AWS_KEY=$(oc get secret backups -n "$NAMESPACE" -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d)
AWS_SECRET=$(oc get secret backups -n "$NAMESPACE" -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 -d)
BUCKET=$(oc get configmap backups -n "$NAMESPACE" -o jsonpath='{.data.BUCKET_NAME}')

echo "restoring dump from bucket $BUCKET..."
oc run "reset-restore-$$" -n "$NAMESPACE" --rm -i --restart=Never --quiet \
    --image="image-registry.openshift-image-registry.svc:5000/uknscr-build/postgresql-backup:latest" \
    --env="PGHOST=postgresql" \
    --env="PGUSER=$PGUSER" --env="PGPASSWORD=$PGPASSWORD" --env="PGDATABASE=$PGDATABASE" \
    --env="AWS_ACCESS_KEY_ID=$AWS_KEY" --env="AWS_SECRET_ACCESS_KEY=$AWS_SECRET" \
    --env="BUCKET_NAME=$BUCKET" \
    ${DUMP_KEY:+--env="DUMP_KEY=$DUMP_KEY"} \
    --command -- python3 /usr/local/bin/restore_helper.py \
    || fail "restore failed"

# 8. Scale the app back up.
"$(dirname "$0")/../prod-upgrade/12-scale-up.sh" "$NAMESPACE"

echo
echo "== Reset complete: $NAMESPACE is back on PG 12 with restored data =="
echo "Run ./scripts/prod-upgrade/00-preflight.sh $NAMESPACE to confirm."
