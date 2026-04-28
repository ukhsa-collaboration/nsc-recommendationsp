#!/usr/bin/env bash
# Step 07 of the prod PG 12->16 upgrade runbook.
# Verify PG 13 after 06-upgrade-12-to-13.sh: server_version is 13.x and
# row counts (exact COUNT(*)) match the preflight baseline.
# See docs/runbooks/prod-pg-upgrade.md section "07 - Verify PG 13".
#
# Usage: scripts/prod-upgrade/07-verify-pg13.sh [namespace]
#   namespace defaults to uknscr-development; uknscr-production prompts for yes.

set -euo pipefail

# Git Bash on Windows otherwise rewrites Unix paths in args to oc.exe
# (e.g. /var/lib/pgsql/data -> C:/Program Files/Git/var/lib/pgsql/data),
# breaking remote-pod commands. No effect on Mac/Linux.
export MSYS_NO_PATHCONV=1

NAMESPACE="${1:-uknscr-development}"
EXPECT_MAJOR="13"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Verify PG $EXPECT_MAJOR against PRODUCTION. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

# Most recent preflight snapshot for this namespace is our baseline.
BASELINE=$(ls -t "/tmp/uknscr-preflight-${NAMESPACE}-"*.txt 2>/dev/null | head -1 || true)
[[ -n "$BASELINE" ]] \
    || fail "no preflight baseline at /tmp/uknscr-preflight-${NAMESPACE}-*.txt -- run 00-preflight before 06"

echo "== Verify PG $EXPECT_MAJOR: $NAMESPACE =="
echo "baseline:         $BASELINE"

PGUSER=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-user}' | base64 -d)
PGPASSWORD=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-password}' | base64 -d)
PGDATABASE=$(oc get secret postgresql -n "$NAMESPACE" -o jsonpath='{.data.database-name}' | base64 -d)
[[ -n "$PGUSER" && -n "$PGPASSWORD" && -n "$PGDATABASE" ]] \
    || fail "could not read postgresql secret in $NAMESPACE"

STAMP=$(date -u +%Y%m%d-%H%M%S)
CURRENT="/tmp/uknscr-verify-pg${EXPECT_MAJOR}-${NAMESPACE}-${STAMP}.txt"

# Verify runs in a side pod (postgresql-backup:latest) because the live
# openshift/postgresql RHEL-8 images don't ship python3.
IMAGE="image-registry.openshift-image-registry.svc:5000/uknscr-build/postgresql-backup:latest"
echo "running restore_verify in side pod..."
oc run "verify-pg${EXPECT_MAJOR}-${STAMP}" -n "$NAMESPACE" \
    --rm -i --restart=Never --quiet \
    --image="$IMAGE" \
    --env="PGHOST=postgresql" \
    --env="PGUSER=$PGUSER" \
    --env="PGPASSWORD=$PGPASSWORD" \
    --env="PGDATABASE=$PGDATABASE" \
    --command -- python3 /usr/local/bin/restore_verify.py \
    > "$CURRENT" 2>&1 \
    || { cat "$CURRENT" >&2; fail "restore_verify failed"; }

NEW_VER=$(grep '^pg_version=' "$CURRENT" | cut -d= -f2)
NEW_MAJOR="${NEW_VER%%.*}"
[[ "$NEW_MAJOR" == "$EXPECT_MAJOR" ]] \
    || fail "expected PG $EXPECT_MAJOR, got $NEW_VER"

# Row-count diff. Both baseline and current emit "schema\ttable\tcount" lines
# via different headings; grep out the count lines and sort before diffing.
baseline_rows=$(grep -E '^[a-z_]+	[a-z_]+	[0-9]+$' "$BASELINE" | sort)
current_rows=$(grep -E '^[a-z_]+	[a-z_]+	[0-9]+$' "$CURRENT" | sort)

DIFF_OUT="/tmp/uknscr-verify-pg${EXPECT_MAJOR}-diff-${STAMP}.txt"
if ! diff <(echo "$baseline_rows") <(echo "$current_rows") > "$DIFF_OUT"; then
    echo "FAIL: row counts differ from baseline:" >&2
    head -30 "$DIFF_OUT" >&2
    exit 1
fi

n_tables=$(echo "$current_rows" | wc -l | tr -d ' ')
echo "pg version:       $NEW_VER"
echo "row counts match baseline ($n_tables user tables)"
echo "verify output:    $CURRENT"
echo "OK"
