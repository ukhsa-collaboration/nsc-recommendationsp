#!/usr/bin/env bash
# Step 02 of the prod PG 12->16 upgrade runbook.
# Poll pg_stat_activity until no client connections remain (only the postmaster
# and internal autovacuum/walwriter workers). If an app connection lingers
# past the timeout we'd rather know before starting the backup/upgrade.
# See docs/runbooks/prod-pg-upgrade.md section "02 - Wait for DB to quiesce".
#
# Usage: scripts/prod-upgrade/02-wait-for-quiet.sh [namespace]
#   namespace defaults to uknscr-development; uknscr-production prompts for yes.

set -euo pipefail

NAMESPACE="${1:-uknscr-development}"
TIMEOUT_SECS="${TIMEOUT_SECS:-120}"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Wait-for-quiet against PRODUCTION. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

POD=$(oc get pod -n "$NAMESPACE" -l deploymentconfig=postgresql \
    -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | awk '{print $1}')
[[ -n "$POD" ]] || fail "no Running postgresql pod in $NAMESPACE"

echo "== Wait for quiet: $NAMESPACE (pod=$POD, timeout=${TIMEOUT_SECS}s) =="

# Count only client connections: exclude autovacuum, logical replication,
# and background workers. The only remaining session should be our psql itself.
SQL="SELECT count(*) FROM pg_stat_activity
     WHERE backend_type='client backend'
       AND pid <> pg_backend_pid();"

deadline=$(( $(date +%s) + TIMEOUT_SECS ))
while :; do
    n=$(oc exec -n "$NAMESPACE" "$POD" -- bash -c \
        "psql -U \"\$POSTGRESQL_USER\" -d \"\$POSTGRESQL_DATABASE\" -tAc \"$SQL\"" 2>/dev/null | tr -d ' ')
    if [[ "$n" =~ ^[0-9]+$ ]] && (( n == 0 )); then
        echo "DB quiet: 0 client backends"
        echo "OK"
        exit 0
    fi
    now=$(date +%s)
    if (( now >= deadline )); then
        echo "still $n client connection(s) after ${TIMEOUT_SECS}s; listing:" >&2
        oc exec -n "$NAMESPACE" "$POD" -- bash -c \
            "psql -U \"\$POSTGRESQL_USER\" -d \"\$POSTGRESQL_DATABASE\" -c \
            \"SELECT pid, application_name, client_addr, state, query_start, left(query, 80) as query FROM pg_stat_activity WHERE backend_type='client backend' AND pid <> pg_backend_pid();\"" >&2
        fail "DB did not quiet within ${TIMEOUT_SECS}s"
    fi
    echo "  $n client connection(s); waiting..."
    sleep 3
done
