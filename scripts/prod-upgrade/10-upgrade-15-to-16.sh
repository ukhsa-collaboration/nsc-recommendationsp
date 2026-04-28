#!/usr/bin/env bash
# Step 10 of the prod PG 12->16 upgrade runbook.
# Final hop: upgrade PG 15 -> 16 by setting POSTGRESQL_UPGRADE=copy on the
# DC and flipping the ImageChange trigger from postgresql:15-c9s to
# postgresql:16-c9s (both namespace-local). The SCL init script inside
# the new pod detects the existing PG 15 data dir and runs pg_upgrade
# in copy mode.
# See docs/runbooks/prod-pg-upgrade.md section "10 - Upgrade 15 -> 16".
#
# Usage: scripts/prod-upgrade/10-upgrade-15-to-16.sh [namespace]
#   namespace defaults to uknscr-development; uknscr-production prompts for yes.

set -euo pipefail

# Git Bash on Windows otherwise rewrites Unix paths in args to oc.exe
# (e.g. /var/lib/pgsql/data -> C:/Program Files/Git/var/lib/pgsql/data),
# breaking remote-pod commands. No effect on Mac/Linux.
export MSYS_NO_PATHCONV=1

NAMESPACE="${1:-uknscr-development}"
FROM_TAG="postgresql:15-c9s"
TO_TAG="postgresql:16-c9s"
FROM_MAJOR="15"
TO_MAJOR="16"

if [[ "$NAMESPACE" == "uknscr-production" ]]; then
    read -rp "Upgrade PG $FROM_MAJOR -> $TO_MAJOR against PRODUCTION. Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || { echo "aborted" >&2; exit 1; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

# Preflight: current pod must be on FROM_MAJOR.
POD=$(oc get pod -n "$NAMESPACE" -l deploymentconfig=postgresql \
    -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | awk '{print $1}')
[[ -n "$POD" ]] || fail "no Running postgresql pod in $NAMESPACE"

CUR_VER=$(oc exec -n "$NAMESPACE" "$POD" -- bash -c \
    'psql -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -tAc "SHOW server_version;"' 2>/dev/null)
CUR_MAJOR="${CUR_VER%%.*}"
[[ "$CUR_MAJOR" == "$FROM_MAJOR" ]] \
    || fail "expected PG $FROM_MAJOR, found $CUR_VER (pod $POD)"

echo "== Upgrade PG $FROM_MAJOR -> $TO_MAJOR: $NAMESPACE =="
echo "current pod:      $POD ($CUR_VER)"

# Pause rollouts so env + trigger changes batch into a single rollout.
echo "pausing DC rollouts..."
oc rollout pause dc/postgresql -n "$NAMESPACE" >/dev/null 2>&1 \
    || oc patch dc postgresql -n "$NAMESPACE" --type=merge -p '{"spec":{"paused":true}}' >/dev/null

echo "setting POSTGRESQL_UPGRADE=copy on DC..."
oc set env dc/postgresql POSTGRESQL_UPGRADE=copy -n "$NAMESPACE" >/dev/null

echo "switching ImageChange trigger: $FROM_TAG -> $TO_TAG..."
oc set triggers dc/postgresql -n "$NAMESPACE" --remove=true \
    --from-image="$FROM_TAG" -c postgresql >/dev/null
oc set triggers dc/postgresql -n "$NAMESPACE" --auto \
    --from-image="$TO_TAG" -c postgresql >/dev/null

echo "resuming DC rollouts..."
oc rollout resume dc/postgresql -n "$NAMESPACE" >/dev/null 2>&1 \
    || oc patch dc postgresql -n "$NAMESPACE" --type=merge -p '{"spec":{"paused":false}}' >/dev/null

# Trigger a fresh rollout explicitly; the pause/resume may or may not have
# done it depending on OCP version.
oc rollout latest dc/postgresql -n "$NAMESPACE" >/dev/null 2>&1 || true

echo "waiting for rollout to PG $TO_MAJOR to complete (timeout 10m)..."
oc rollout status dc/postgresql -n "$NAMESPACE" --timeout=10m \
    || { echo "rollout logs:"; oc logs -n "$NAMESPACE" -l deploymentconfig=postgresql --tail=60; fail "rollout did not complete"; }

NEW_POD=$(oc get pod -n "$NAMESPACE" -l deploymentconfig=postgresql \
    -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | awk '{print $1}')
[[ -n "$NEW_POD" ]] || fail "no Running postgresql pod after rollout"
[[ "$NEW_POD" != "$POD" ]] || fail "pod name unchanged; rollout may not have happened ($POD)"

NEW_VER=$(oc exec -n "$NAMESPACE" "$NEW_POD" -- bash -c \
    'psql -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -tAc "SHOW server_version;"' 2>/dev/null)
NEW_MAJOR="${NEW_VER%%.*}"
[[ "$NEW_MAJOR" == "$TO_MAJOR" ]] \
    || fail "expected PG $TO_MAJOR, found $NEW_VER after upgrade"

echo "new pod:          $NEW_POD ($NEW_VER)"

# Look for the SCL upgrade-complete log line.
if oc logs -n "$NAMESPACE" "$NEW_POD" | grep -qiE "upgrade.*(successful|complete)"; then
    echo "pod log confirms upgrade-complete line"
else
    echo "WARN: no upgrade-complete line found in pod log (may be fine if SCL logs differently on this version)" >&2
fi

# Remove POSTGRESQL_UPGRADE so subsequent restarts don't re-run the upgrade.
# (SCL should no-op if data is already at target version, but belt-and-braces.)
echo "unsetting POSTGRESQL_UPGRADE..."
oc set env dc/postgresql POSTGRESQL_UPGRADE- -n "$NAMESPACE" >/dev/null
oc rollout status dc/postgresql -n "$NAMESPACE" --timeout=5m >/dev/null

echo "OK"
