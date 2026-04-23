#!/usr/bin/env bash
# Step 05 of the prod PG 12->16 upgrade runbook.
# Take an ODF Ceph RBD VolumeSnapshot of the postgresql PVC. Belt-and-braces
# alongside the step-03 S3 dump: a snapshot lets us revert the whole PVC
# to the pre-upgrade state in a single API call if the upgrade later goes
# wrong in a way the dump-restore can't easily reach.
# See docs/runbooks/prod-pg-upgrade.md section "05 - PV snapshot".
#
# Usage: scripts/prod-upgrade/05-snapshot-pv.sh [namespace]
#   namespace defaults to uknscr-development; uknscr-production prompts for yes.
#
# Does NOT clean up old snapshots. They live until manually deleted via
# oc delete volumesnapshot -n <ns> postgresql-preupgrade-*.

set -euo pipefail

NAMESPACE="${1:-uknscr-development}"
SNAPSHOT_CLASS="${SNAPSHOT_CLASS:-ocs-storagecluster-rbdplugin-snapclass}"
PVC_NAME="${PVC_NAME:-postgresql}"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Snapshot PRODUCTION postgresql PVC. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

# RBAC preflight. Fail fast with a clear message rather than a generic
# "forbidden" later; the runbook treats snapshot as optional so a skip is
# a legitimate path (document in the runbook and rely on the dump).
if ! oc auth can-i create volumesnapshot -n "$NAMESPACE" 2>/dev/null | grep -q yes; then
    fail "no VolumeSnapshot create permission in $NAMESPACE (skip acceptable; rely on step-03 dump)"
fi

# Preflight: PVC exists, snapshot class exists.
oc get pvc "$PVC_NAME" -n "$NAMESPACE" >/dev/null 2>&1 \
    || fail "PVC $PVC_NAME not found in $NAMESPACE"
oc get volumesnapshotclass "$SNAPSHOT_CLASS" >/dev/null 2>&1 \
    || fail "VolumeSnapshotClass $SNAPSHOT_CLASS not found"

STAMP=$(date -u +%Y%m%d-%H%M%S)
SNAPSHOT="${PVC_NAME}-preupgrade-${STAMP}"

echo "== PV snapshot: $NAMESPACE =="
echo "PVC:              $PVC_NAME"
echo "snapshot class:   $SNAPSHOT_CLASS"
echo "snapshot name:    $SNAPSHOT"

oc apply -n "$NAMESPACE" -f - <<EOF >/dev/null
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: $SNAPSHOT
  labels:
    uknscr.purpose: prod-pg-upgrade-preupgrade
    uknscr.timestamp: "$STAMP"
spec:
  volumeSnapshotClassName: $SNAPSHOT_CLASS
  source:
    persistentVolumeClaimName: $PVC_NAME
EOF

echo "waiting for snapshot ReadyToUse (timeout 5m)..."
deadline=$(( $(date +%s) + 300 ))
while :; do
    ready=$(oc get volumesnapshot "$SNAPSHOT" -n "$NAMESPACE" \
        -o jsonpath='{.status.readyToUse}' 2>/dev/null || echo "")
    err=$(oc get volumesnapshot "$SNAPSHOT" -n "$NAMESPACE" \
        -o jsonpath='{.status.error.message}' 2>/dev/null || echo "")
    [[ "$ready" == "true" ]] && break
    if [[ -n "$err" ]]; then
        fail "snapshot error: $err"
    fi
    if (( $(date +%s) >= deadline )); then
        oc describe volumesnapshot "$SNAPSHOT" -n "$NAMESPACE" >&2
        fail "snapshot not ReadyToUse after 5m"
    fi
    sleep 3
done

SIZE=$(oc get volumesnapshot "$SNAPSHOT" -n "$NAMESPACE" \
    -o jsonpath='{.status.restoreSize}')
CREATION=$(oc get volumesnapshot "$SNAPSHOT" -n "$NAMESPACE" \
    -o jsonpath='{.status.creationTime}')

echo "ready at:         $CREATION"
echo "restore size:     $SIZE"
echo
echo "To revert the PVC to this snapshot later:"
echo "  oc scale dc postgresql --replicas=0 -n $NAMESPACE"
echo "  oc delete pvc $PVC_NAME -n $NAMESPACE"
echo "  oc apply -f - <<YAML"
echo "apiVersion: v1"
echo "kind: PersistentVolumeClaim"
echo "metadata: {name: $PVC_NAME, namespace: $NAMESPACE}"
echo "spec:"
echo "  accessModes: [ReadWriteOnce]"
echo "  resources: {requests: {storage: $SIZE}}"
echo "  storageClassName: ocs-storagecluster-ceph-rbd"
echo "  dataSource: {apiGroup: snapshot.storage.k8s.io, kind: VolumeSnapshot, name: $SNAPSHOT}"
echo "YAML"
echo "  oc scale dc postgresql --replicas=1 -n $NAMESPACE"
echo "OK"
