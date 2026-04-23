#!/usr/bin/env bash
# Step 03 of the prod PG 12->16 upgrade runbook.
# Trigger a manual backup NOW (fresh, known-quiet dump). Not relying on the 02:30 UTC daily run.
# See docs/runbooks/prod-pg-upgrade.md section "03 - Take pre-upgrade backup".
#
# Usage: scripts/prod-upgrade/03-manual-backup.sh [namespace]
#   namespace defaults to uknscr-development. uknscr-production prompts for yes.
#
# Parses the backup pod log to report the S3 key + size. Using the log directly
# (rather than a bucket LIST) sidesteps NooBaa's eventual-consistency window
# and is the authoritative record of what was uploaded.

set -euo pipefail

NAMESPACE="${1:-uknscr-development}"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Manual backup against PRODUCTION. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

oc get cronjob postgresql-backup -n "$NAMESPACE" >/dev/null 2>&1 \
    || fail "no postgresql-backup cronjob in $NAMESPACE"

STAMP=$(date -u +%Y%m%d-%H%M%S)
JOB="manual-backup-${STAMP}"

echo "== Manual backup: $NAMESPACE =="
echo "triggering job:   $JOB"

oc create job "$JOB" --from=cronjob/postgresql-backup -n "$NAMESPACE" >/dev/null

if ! oc wait --for=condition=complete "job/$JOB" -n "$NAMESPACE" --timeout=10m 2>&1 | grep -q "condition met"; then
    echo "job did not complete within 10 min; pod logs:" >&2
    oc logs -n "$NAMESPACE" "job/$JOB" --tail=50 >&2 || true
    fail "backup job $JOB did not complete"
fi

LOG=$(oc logs -n "$NAMESPACE" "job/$JOB")
VERIFIED_LINE=$(echo "$LOG" | grep "backup verified:" | tail -1)
[[ -n "$VERIFIED_LINE" ]] || {
    echo "$LOG" >&2
    fail "backup pod did not log a 'backup verified:' line"
}

# Parse: "... backup verified: s3://bucket/key (NNN bytes)"
S3_URL=$(echo "$VERIFIED_LINE" | sed -E 's/.*backup verified: (s3:\/\/[^ ]+).*/\1/')
SIZE=$(echo "$VERIFIED_LINE" | sed -E 's/.*\(([0-9]+) bytes\).*/\1/')

(( SIZE > 0 )) || fail "backup size reported as 0 bytes"

echo "job completed:    $JOB"
echo "s3 url:           $S3_URL"
echo "size:             $SIZE bytes"
echo "OK"
