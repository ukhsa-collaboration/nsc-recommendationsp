#!/usr/bin/env bash
# List objects in a uknscr backup bucket via a one-shot helper pod.
#
# Usage: scripts/ops/list-bucket.sh [namespace]
#   namespace defaults to uknscr-development
#   if namespace is uknscr-production, prompts for yes confirmation
#
# Requires: oc logged in; edit access in the target namespace to read the
# backups secret and create the helper pod. Runs the list_bucket module
# baked into the postgresql-backup image (see deploy/list_bucket.py).

set -euo pipefail

NAMESPACE="${1:-uknscr-development}"
IMAGE="image-registry.openshift-image-registry.svc:5000/uknscr-build/postgresql-backup:latest"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "About to list prod backup bucket. Type 'yes' to continue: " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "aborted" >&2
        exit 1
    fi
fi

AWS_KEY=$(oc get secret backups -n "$NAMESPACE" -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d)
AWS_SECRET=$(oc get secret backups -n "$NAMESPACE" -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 -d)
BUCKET=$(oc get configmap backups -n "$NAMESPACE" -o jsonpath='{.data.BUCKET_NAME}')

oc run "list-bucket-$$" -n "$NAMESPACE" --rm -i --restart=Never --quiet \
    --image="$IMAGE" \
    --env="AWS_ACCESS_KEY_ID=$AWS_KEY" \
    --env="AWS_SECRET_ACCESS_KEY=$AWS_SECRET" \
    --env="BUCKET_NAME=$BUCKET" \
    --command -- python3 /usr/local/bin/list_bucket.py
