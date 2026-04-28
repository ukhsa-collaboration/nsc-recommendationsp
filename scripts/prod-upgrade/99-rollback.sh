#!/usr/bin/env bash
# Rollback guidance for the prod PG 12->16 upgrade.
# This script does NOT auto-rollback. It prints the recovery steps for
# whichever failure point you hit, and runs the safe parts on request.
# Destructive ops (delete PVC, revert image tag) are always printed as
# commands the runner copy-pastes, never executed by this script.
#
# See docs/runbooks/prod-pg-upgrade.md section "Rollback".
#
# Usage: scripts/prod-upgrade/99-rollback.sh [namespace] <stage>
#   namespace defaults to uknscr-development; uknscr-production prompts for yes.
#   stage is one of: scale-down, pre-upgrade, upgrade-12-to-13,
#                    upgrade-13-to-15, upgrade-15-to-16, post-upgrade.
#
# Exits 0 after printing guidance. Does not modify cluster state (except
# the --scale-up shortcut which is non-destructive).

set -euo pipefail

# Git Bash on Windows otherwise rewrites Unix paths in args to oc.exe
# (e.g. /var/lib/pgsql/data -> C:/Program Files/Git/var/lib/pgsql/data),
# breaking remote-pod commands. No effect on Mac/Linux.
export MSYS_NO_PATHCONV=1

usage() {
    sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
}

NAMESPACE=""
STAGE=""
DO_SCALE_UP=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scale-up) DO_SCALE_UP=true; shift ;;
        -h|--help) usage ;;
        -*) echo "unknown flag: $1" >&2; usage ;;
        *)
            if [[ -z "$NAMESPACE" ]]; then NAMESPACE="$1"
            elif [[ -z "$STAGE" ]]; then STAGE="$1"
            else echo "unexpected arg: $1" >&2; usage
            fi
            shift
            ;;
    esac
done

NAMESPACE="${NAMESPACE:-uknscr-development}"
[[ -n "$STAGE" ]] || { echo "missing <stage> argument" >&2; usage; }

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Rollback guidance for PRODUCTION stage=$STAGE. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

echo "== Rollback guidance: $NAMESPACE, stage=$STAGE =="
echo

case "$STAGE" in
    scale-down)
        cat <<EOF
You're at 01-scale-down or 02-wait-for-quiet; nothing has changed on the DB.
Recovery: just scale the app back to its prior replica counts.

Run:
    ./scripts/prod-upgrade/12-scale-up.sh $NAMESPACE
EOF
        if $DO_SCALE_UP; then
            echo; echo "--scale-up flag set; running 12-scale-up.sh..."
            exec "$(dirname "$0")/12-scale-up.sh" "$NAMESPACE"
        fi
        ;;

    pre-upgrade)
        cat <<EOF
You're at 03-manual-backup, 04-restore-drill, or 05-snapshot-pv.
No PG major version change yet; data dir is still the source version.
Recovery: scale the app back up; the backup or snapshot failure itself
is worth investigating but does not require data recovery.

Run:
    ./scripts/prod-upgrade/12-scale-up.sh $NAMESPACE
EOF
        if $DO_SCALE_UP; then
            echo; echo "--scale-up flag set; running 12-scale-up.sh..."
            exec "$(dirname "$0")/12-scale-up.sh" "$NAMESPACE"
        fi
        ;;

    upgrade-12-to-13|upgrade-13-to-15|upgrade-15-to-16)
        case "$STAGE" in
            upgrade-12-to-13) FROM="openshift/postgresql:12-el8"; FROMVER=12 ;;
            upgrade-13-to-15) FROM="openshift/postgresql:13-el8"; FROMVER=13 ;;
            upgrade-15-to-16) FROM="postgresql:15-c9s";            FROMVER=15 ;;
        esac
        cat <<EOF
pg_upgrade errored mid-run. SCL's error handler (rm -rf \$PGDATA_new) has
already cleaned up the partial new data dir; the old PG $FROMVER data dir
on the PVC is intact. Recovery is cheap: revert the DC trigger and unset
POSTGRESQL_UPGRADE, then let the DC roll a fresh pod on PG $FROMVER.

Run (copy-paste):
    oc set env dc/postgresql POSTGRESQL_UPGRADE- -n $NAMESPACE
    # Remove whatever trigger this upgrade hop added:
    oc set triggers dc/postgresql -n $NAMESPACE --remove=true --from-image=<target-tag> -c postgresql
    # Restore the source trigger:
    oc set triggers dc/postgresql -n $NAMESPACE --auto --from-image=$FROM -c postgresql
    oc rollout latest dc/postgresql -n $NAMESPACE
    oc rollout status dc/postgresql -n $NAMESPACE --timeout=5m
    # Sanity check:
    POD=\$(oc get pod -n $NAMESPACE -l deploymentconfig=postgresql -o jsonpath='{.items[0].metadata.name}')
    oc exec -n $NAMESPACE \$POD -- psql -U \$POSTGRESQL_USER -d \$POSTGRESQL_DATABASE -c 'SHOW server_version;'

Then:
    ./scripts/prod-upgrade/12-scale-up.sh $NAMESPACE

Data loss: none (old data dir was never touched).
EOF
        ;;

    post-upgrade)
        cat <<EOF
pg_upgrade succeeded but a later verify / smoke test failed. SCL has
already deleted the old data dir (rm -rf \$PGDATA_old in common.sh).
Recovery path is dump restore into a fresh PVC.

REQUIREMENTS:
  - A usable pre-upgrade dump (the one from 03-manual-backup.sh, OR an
    earlier daily from the backup CronJob). The dump was taken post-
    scale-down + post-quiet, so restoring it loses zero app data.
  - The corresponding backup bucket credentials.
  - Optional: a VolumeSnapshot from 05-snapshot-pv.sh for an even
    faster revert; see section at the bottom.

Steps (app is assumed already scaled to 0 from 01-scale-down):

1. Scale postgresql DC to 0 and wipe the current PVC:

    oc scale dc postgresql --replicas=0 -n $NAMESPACE
    oc wait --for=delete pod -n $NAMESPACE -l deploymentconfig=postgresql --timeout=2m
    oc delete pvc postgresql -n $NAMESPACE

2. Recreate an empty PVC of the same size + storage class:

    oc apply -n $NAMESPACE -f - <<YAML
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: postgresql
    spec:
      accessModes: [ReadWriteOnce]
      resources:
        requests:
          storage: 10Gi
      storageClassName: ocs-storagecluster-ceph-rbd
    YAML

3. Revert DC triggers to the ORIGINAL source version (PG 12-el8):

    for tag in postgresql:16-c9s postgresql:15-c9s openshift/postgresql:13-el8; do
        oc set triggers dc/postgresql -n $NAMESPACE --remove=true --from-image=\$tag -c postgresql 2>/dev/null || true
    done
    oc set triggers dc/postgresql -n $NAMESPACE --auto --from-image=openshift/postgresql:12-el8 -c postgresql
    oc set env dc/postgresql POSTGRESQL_UPGRADE- -n $NAMESPACE
    oc scale dc postgresql --replicas=1 -n $NAMESPACE
    oc rollout status dc/postgresql -n $NAMESPACE --timeout=5m

4. Restore the pre-upgrade dump via a helper pod. DUMP_KEY is the
   specific uknscr-<date>.dump you took in step 03; find it in the
   backup pod log or list the bucket. Fetch PG + S3 creds from the
   namespace's secrets/configmap.

    PGUSER=\$(oc get secret postgresql -n $NAMESPACE -o jsonpath='{.data.database-user}' | base64 -d)
    PGPASSWORD=\$(oc get secret postgresql -n $NAMESPACE -o jsonpath='{.data.database-password}' | base64 -d)
    PGDATABASE=\$(oc get secret postgresql -n $NAMESPACE -o jsonpath='{.data.database-name}' | base64 -d)
    AWS_KEY=\$(oc get secret backups -n $NAMESPACE -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d)
    AWS_SECRET=\$(oc get secret backups -n $NAMESPACE -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 -d)
    BUCKET=\$(oc get configmap backups -n $NAMESPACE -o jsonpath='{.data.BUCKET_NAME}')

    oc run restore-\$\$ -n $NAMESPACE --rm -i --restart=Never --quiet \\
        --image=image-registry.openshift-image-registry.svc:5000/uknscr-build/postgresql-backup:latest \\
        --env=PGHOST=postgresql \\
        --env=PGUSER=\$PGUSER --env=PGPASSWORD=\$PGPASSWORD --env=PGDATABASE=\$PGDATABASE \\
        --env=AWS_ACCESS_KEY_ID=\$AWS_KEY --env=AWS_SECRET_ACCESS_KEY=\$AWS_SECRET \\
        --env=BUCKET_NAME=\$BUCKET \\
        --env=DUMP_KEY=uknscr-YYYY-MM-DD_HHMMSS.dump \\
        --command -- python3 /usr/local/bin/restore_helper.py

5. Scale the app back up:

    ./scripts/prod-upgrade/12-scale-up.sh $NAMESPACE

Data loss: zero (backup was taken after scale-down + wait-for-quiet).

----
FAST PATH (if 05-snapshot-pv.sh succeeded):

Instead of steps 2-4 above, restore the PVC directly from the snapshot:

    SNAPSHOT=\$(oc get volumesnapshot -n $NAMESPACE -l uknscr.purpose=prod-pg-upgrade-preupgrade --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1:].metadata.name}')
    oc delete pvc postgresql -n $NAMESPACE
    oc apply -n $NAMESPACE -f - <<YAML
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: postgresql
    spec:
      accessModes: [ReadWriteOnce]
      resources:
        requests:
          storage: 10Gi
      storageClassName: ocs-storagecluster-ceph-rbd
      dataSource:
        apiGroup: snapshot.storage.k8s.io
        kind: VolumeSnapshot
        name: \$SNAPSHOT
    YAML

Then skip step 4 (the snapshot already contains pre-upgrade data) and
proceed with step 5 (scale-up).
EOF
        ;;

    *)
        echo "unknown stage: $STAGE" >&2
        usage
        ;;
esac
