# Prod PG 12 -> 16 Upgrade Runbook

**Target date:** 2026-04-30 (or 2026-05-01)
**Author:** Devin Barry
**Runner:** An `uknscr-editors` group member on a live call with the author
**Expected downtime:** ~10 min of user-visible 5xx (staging rehearsal at 22 MB clocked ~6 min wall-clock; prod is ~3.3 MB)

This file is the deep reference for the upgrade. The Confluence page
"PG 12 -> 16 dress rehearsal" is the operational walkthrough; come here
for proceed/stop gates per step, the rollback decision tree, known
risks, and post-upgrade cleanup.

## Before you start

- Clone `nsc-recommendationsp`, check out `feat/prod-upgrade-scripts`.
- `oc login` to ocp-az-uks.
- `oc whoami` and `oc project uknscr-production` to confirm you're pointed at the right namespace.
- Confirm you're on a screen-share call with Devin.
- Read this runbook top-to-bottom before touching anything.

## Steps

Each heading maps to a numbered script in `scripts/prod-upgrade/`. Run them
in order; wait for each to exit cleanly before running the next. The
"Proceed if" / "Stop if" lines are the explicit decision gates.

### 00 - Preflight

*Purpose:* Validate cluster state and snapshot a row-count baseline that
07/09/11 verify against. Writes `/tmp/uknscr-preflight-<ns>-<ts>.txt`
with PG version, db size, PVC usage, DC trigger count, exact
COUNT(*) per user table, and a schema hash.
*Script:* `./scripts/prod-upgrade/00-preflight.sh uknscr-production`
*Proceed if:* script prints `OK`; pg version matches the source major
(12.x for the first run); `dc img triggers: 1`; PVC <50% used.
*Stop if:* namespace inaccessible, no Running postgresql pod, psql
connection failure, PVC ≥50% used (copy-mode pg_upgrade needs ~2x DB
size free), or the restore_verify side pod fails.

### 01 - Scale down workers

*Purpose:* Stop celery-beat, celery-worker, and django-webpack so no
new writes hit the DB during the upgrade. App goes 5xx — expected.
Records the prior replica counts to a snapshot file so 12 can restore
them.
*Script:* `./scripts/prod-upgrade/01-scale-down.sh uknscr-production`
*Proceed if:* all three DCs report scale `0`; pods Terminate within 2 min;
`scale snapshot:` line printed.
*Stop if:* any DC fails to scale, or pods stuck Terminating past 2 min
(typically a celery worker holding a long task — `oc delete pod --force`).

### 02 - Wait for DB to quiesce

*Purpose:* Confirm no client backends remain (only postmaster + internal
workers), then re-run preflight against the now-quiet DB so the verify
baseline is captured at the exact moment writes stopped. The verify
scripts pick the most-recent baseline file, so this newer snapshot wins
over the step-00 one.
*Script:* `./scripts/prod-upgrade/02-wait-for-quiet.sh uknscr-production`
*Proceed if:* `DB quiet: 0 client backends`, then the chained preflight
prints `OK` with a fresh snapshot path.
*Stop if:* client backends non-zero after 120s — script lists the
holdouts; usually a stuck celery worker. Force-delete the pod and
re-run 02.

### 03 - Pre-upgrade backup

*Purpose:* Trigger a manual backup CronJob run; uploads a `pg_dump
--format=custom` to the prod backups bucket. This is the rollback
floor — if every other step fails, this dump is what we restore from.
Taken AFTER 01 + 02 so it captures a quiet, consistent state.
*Script:* `./scripts/prod-upgrade/03-manual-backup.sh uknscr-production`
*Proceed if:* `s3 url:` printed; size is within ~20% of the most recent
scheduled backup (~3.3 MB on prod). **Note the dump key** — write it
on the call notes.
*Stop if:* backup job fails, `size: 0`, or wildly small (likely a
connection problem or a query that bombed the dump).

### 04 - Restore drill

*Purpose:* Prove the just-taken dump is restorable. Spins a throwaway
pod from `postgresql-backup:latest`, fetches the dump, restores it
into an ephemeral PG 16 cluster, runs `restore_verify.py` against the
result. Cleans up after itself.
*Script:* `./scripts/prod-upgrade/04-restore-drill.sh uknscr-production`
*Proceed if:* `verify output:` file written; `drill pg version: 16.x`;
schema hash printed.
*Stop if:* ANY failure. An untestable backup is not a backup. Don't
proceed with the upgrade — fix the backup pipeline first.

### 05 - PV snapshot

*Purpose:* Belt-and-braces. Creates an ODF Ceph RBD VolumeSnapshot of
the postgresql PVC. Sub-second on RBD; gives a recovery option that
doesn't require dump-restore in the catastrophic case.
*Script:* `./scripts/prod-upgrade/05-snapshot-pv.sh uknscr-production`
*Proceed if:* `ready at:` printed within ~5 sec; `restore size:`
matches PVC capacity (10Gi on prod).
*Stop if:* snapshot stuck not-Ready after 5 min — the snapclass or
storage backend has a problem. The dump from step 03 is still good
as a fallback recovery path; you can choose to proceed without the
snapshot, but flag it on the call.

### 06 - Upgrade 12 -> 13

*Purpose:* First hop. Pauses DC rollouts, sets `POSTGRESQL_UPGRADE=copy`,
patches the ImageChange trigger to `openshift/postgresql:13-el8`,
resumes rollouts, waits for the new pod, then unsets `POSTGRESQL_UPGRADE`.
SCL's init script runs `pg_upgrade --link=false` (copy mode) on first
boot when it sees the env var + version mismatch.
*Script:* `./scripts/prod-upgrade/06-upgrade-12-to-13.sh uknscr-production`
*Proceed if:* `new pod: ... (13.x)`, `pod log confirms upgrade-complete
line`, both rollouts complete within 10 min total. (Two rollouts are
expected — image change first, config change when `POSTGRESQL_UPGRADE`
is unset at the end. ~30 sec extra per hop, cosmetic.)
*Stop if:* rollout times out, pod CrashLoopBackOff, `pg_upgrade` error
in logs. **Mid-upgrade failure path** in Rollback section — old data
dir is intact.

### 07 - Verify PG 13

*Purpose:* Confirm pg version is 13.x and row counts match the baseline
from step 02 (the post-quiet rebaseline, not the original step-00 one).
Schema hash is recorded but not strictly diffed across major versions
(pg_dump output format changes per version).
*Script:* `./scripts/prod-upgrade/07-verify-pg13.sh uknscr-production`
*Proceed if:* `pg version: 13.x` and `row counts match baseline`.
*Stop if:* version mismatch or row counts differ. **Post-success failure
path** in Rollback section — old data dir is GONE; restore from the
step-03 dump.

### 08 - Upgrade 13 -> 15

*Purpose:* Second hop. Same pattern as 06 but the target tag is
`postgresql:15-c9s` (namespace-local SCL c9s image). SCL skips PG 14;
13 → 15 is one `pg_upgrade` step.
*Script:* `./scripts/prod-upgrade/08-upgrade-13-to-15.sh uknscr-production`
*Proceed if / Stop if:* same as 06, except `new pod: ... (15.x)`.

### 09 - Verify PG 15

Same as 07 but expecting 15.x.
*Script:* `./scripts/prod-upgrade/09-verify-pg15.sh uknscr-production`

### 10 - Upgrade 15 -> 16

*Purpose:* Final hop. Same pattern as 06; target tag is
`postgresql:16-c9s`. Once this completes, prod is on the target version.
*Script:* `./scripts/prod-upgrade/10-upgrade-15-to-16.sh uknscr-production`
*Proceed if / Stop if:* same as 06, except `new pod: ... (16.x)`.

### 11 - Verify PG 16

Same as 07 but expecting 16.x. **This is the final verify gate — passing
this means the upgrade succeeded; failing this is a post-success failure
and the rollback path is dump-restore.**
*Script:* `./scripts/prod-upgrade/11-verify-pg16.sh uknscr-production`

### 12 - Scale back up

*Purpose:* Restore django-webpack, celery-worker, celery-beat to their
pre-upgrade replica counts (read from the snapshot 01 wrote). Waits for
each rollout to complete.
*Script:* `./scripts/prod-upgrade/12-scale-up.sh uknscr-production`
*Proceed if:* `all app DCs restored and Ready`; `/_health/` returns 200
on the django-webpack pods; route returns expected page.
*Stop if:* a DC fails to roll out within 10 min, or app pods
CrashLoopBackOff (likely Django-PG-version-compat regression — but the
Django + PG 16 combo was validated end-to-end on dev 2026-04-23 and
staging 2026-04-27).

## Rollback

*Script:* `./scripts/prod-upgrade/99-rollback.sh uknscr-production <stage>`

The rollback strategy depends on *where* the upgrade failed. Important
context on `POSTGRESQL_UPGRADE=copy` semantics: SCL's init script runs
`pg_upgrade --link=false` (copy mode), so the old data dir is intact
*while pg_upgrade runs*. But on success SCL itself does
`rm -rf $PGDATA_old && mv $PGDATA_new $PGDATA` and the old cluster is
gone. Confirmed by reading
`/usr/share/container-scripts/postgresql/common.sh`. So the rollback
path differs between mid-upgrade failure and post-upgrade failure.

### If 06/08/10 exits non-zero (pg_upgrade failed mid-run)

SCL's error handler removes the partial new data dir
(`rm -rf $PGDATA_new`). The old data dir is still at `$PGDATA` untouched.
Recovery:

1. `oc set env dc/postgresql POSTGRESQL_UPGRADE- -n uknscr-production`
2. `oc set triggers` to remove the failed target tag and restore the
   source tag (e.g. revert trigger to `openshift/postgresql:12-el8`).
3. `oc rollout latest dc/postgresql -n uknscr-production`
4. New pod comes up on source version with intact data dir. **Zero data loss.**

### If a verify step (07/09/11) fails OR app regression discovered after rollout

`pg_upgrade` already ran successfully so the old data dir is gone. Path:

1. `./scripts/prod-upgrade/01-scale-down.sh uknscr-production` (app down again).
2. Scale postgresql DC to 0, delete its PVC, recreate an empty PVC of
   the same size + storage class (10Gi, `ocs-storagecluster-ceph-rbd`).
3. Revert DC trigger to the source version (`openshift/postgresql:12-el8`).
4. Scale postgresql DC to 1 -> fresh empty PG 12 pod.
5. Restore the dump taken by `03-manual-backup.sh` using
   `restore_helper.py` (spin a helper pod with `PGHOST=postgresql`,
   the prod postgresql secret, the prod backups bucket creds, and
   `DUMP_KEY=<the key from step 03>`).
6. `./scripts/prod-upgrade/12-scale-up.sh uknscr-production`.
7. Verify app loads.

**Data loss window = 0** because 03 ran *after* 01-scale-down + 02-wait-for-quiet,
so no writes happened between the backup and now.

### Catastrophic PVC corruption

If `05-snapshot-pv.sh` succeeded (VolumeSnapshot available), revert the
PVC from the snapshot (commands are printed by the script as the
`To revert the PVC to this snapshot later:` block). Otherwise fall back
to the dump-restore path above.

### When in doubt

Get Devin on a call before touching anything. The rollback paths are
narrow and the wrong one (e.g. wiping a PVC when the old data dir is
still good) makes recovery harder.

## Known risks

- **Stuck app connection holds 02 past timeout.** Celery workers
  occasionally don't shut down cleanly within 01's 2-min wait. If 02
  fails with `still N client connection(s)`, the script lists the
  holdouts; force-delete the still-running pods (`oc delete pod
  --force --grace-period=0`) and re-run 02.
- **DC trigger accumulation.** Each upgrade hop replaces the matching
  ImageChange trigger; if the DC has multiple stale triggers from prior
  hand-patches, the replacement might not match the right one. Preflight
  prints `dc img triggers:` — should be 1 going into step 06. If higher,
  trim with `oc set triggers --remove` before proceeding.
- **Two-rollout pattern.** Each upgrade step (06/08/10) triggers TWO
  rollouts: ImageChange first, then ConfigChange when `POSTGRESQL_UPGRADE`
  is unset at the end. Adds ~30 sec per hop. Visual noise, not a failure
  mode.
- **pg_dump major-version mismatch.** The schema hash in 07/09/11 may
  show `unavailable` if pg_dump in the postgresql-backup image is older
  than the server. Row counts are the real verify gate; a missing
  schema hash on an intermediate hop is not a stop condition.
- **PVC immutable-field drift.** Dev's postgresql PVC has a permanent
  OutOfSync state in ArgoCD (`storageClassName`). Pre-existing,
  harmless. Don't try to "fix" it during the upgrade — manifest is
  immutable post-creation. Same may surface on staging/prod after their
  PVC is created via ArgoCD instead of the live patch.
- **NooBaa S3 LIST eventual consistency.** `03-manual-backup.sh` parses
  the backup pod's log line (`backup verified: s3://...`) rather than
  LISTing the bucket, sidestepping a race where a fresh dump isn't
  immediately visible. Don't replace it with a LIST.

## Post-upgrade cleanup

- File MR B in `uknscr-k8s` to update `production/postgresql.yaml`: DC
  trigger from `openshift/postgresql:12-el8` to namespace-local
  `postgresql:16-c9s`. Sync ArgoCD `uknscr-production` after merge.
- File MR C: revert `uknscr-k8s/build/postgresql-backup.yaml`
  BuildConfig `ref` from `feat/prod-upgrade-scripts` to its pre-sprint
  default (`feat/backup-image` or whatever has landed on `develop` by
  then).
- Drop the step-05 VolumeSnapshot after 7 days if no issues surface.
- Keep the step-03 dump in the bucket; the 90-day lifecycle will age it
  out.
- Roll `feat/prod-upgrade-scripts` up into `feat/backup-image` /
  `develop` once the dust has settled.
