# Prod PG 12 -> 16 Upgrade Runbook

**Target date:** 2026-04-30 (contingent on Fri 2026-04-24 staging rehearsal)
**Author:** Devin Barry
**Runner:** An `uknscr-editors` group member on a live call with the author
**Expected downtime:** ~15-30 min of user-visible 5xx

## Before you start

- Clone `nsc-recommendationsp`, check out `feat/prod-upgrade-scripts`.
- `oc login` to ocp-az-uks via the usual tunnel setup.
- Confirm you're on a screen-share call with Devin.
- Read this runbook top-to-bottom before touching anything.

## Steps

Each heading maps to a numbered script in `scripts/prod-upgrade/`. Run them in order.

### 00 - Preflight

*Purpose:* Verify the cluster, branch, and image are in the expected state.
*Script:* `./scripts/prod-upgrade/00-preflight.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 01 - Scale down workers

*Purpose:* Stop celery-beat and celery-worker so no new jobs fire during upgrade.
*Script:* `./scripts/prod-upgrade/01-scale-down.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 02 - Wait for DB to quiesce

*Purpose:* Confirm no active non-idle connections before taking the pre-upgrade backup.
*Script:* `./scripts/prod-upgrade/02-wait-for-quiet.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 03 - Take pre-upgrade backup

*Purpose:* Fresh S3 dump, known-quiet state. Not relying on 02:30 UTC daily.
*Script:* `./scripts/prod-upgrade/03-manual-backup.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 04 - Restore drill

*Purpose:* Prove the just-taken dump is restorable. Scratch namespace, ephemeral PG pod.
*Script:* `./scripts/prod-upgrade/04-restore-drill.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 05 - PV snapshot

*Purpose:* Belt-and-braces. ODF Ceph RBD VolumeSnapshot of postgresql PVC.
*Script:* `./scripts/prod-upgrade/05-snapshot-pv.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 06 - Upgrade 12 -> 13

*Purpose:* Patch DeploymentConfig image tag; SCL image auto-upgrades with POSTGRESQL_UPGRADE=copy.
*Script:* `./scripts/prod-upgrade/06-upgrade-12-to-13.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 07 - Verify PG 13

*Purpose:* Row counts, log grep for upgrade-complete line, connection check.
*Script:* `./scripts/prod-upgrade/07-verify-pg13.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 08 - Upgrade 13 -> 15

*Purpose:* Second hop. Same pattern as step 06.
*Script:* `./scripts/prod-upgrade/08-upgrade-13-to-15.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 09 - Verify PG 15

*Purpose:* Same as step 07 but at an intermediate version.
*Script:* `./scripts/prod-upgrade/09-verify-pg15.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 10 - Upgrade 15 -> 16

*Purpose:* Final hop to PG 16 (max EOL distance). Same pattern as step 06.
*Script:* `./scripts/prod-upgrade/10-upgrade-15-to-16.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 11 - Verify PG 16

*Purpose:* Same as step 07 but at the final version.
*Script:* `./scripts/prod-upgrade/11-verify-pg16.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 12 - Scale back up

*Purpose:* django-webpack, celery-worker, celery-beat back to replica counts.
*Script:* `./scripts/prod-upgrade/12-scale-up.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

## Rollback

*Script:* `./scripts/prod-upgrade/99-rollback.sh uknscr-production <stage>`

The rollback strategy depends on *where* the upgrade failed. Important
context on `POSTGRESQL_UPGRADE=copy` semantics: SCL's init script runs
`pg_upgrade --link=false` (copy mode) so the old data dir is intact *while
pg_upgrade runs*, but on success SCL itself does `rm -rf $PGDATA_old &&
mv $PGDATA_new $PGDATA` and deletes the old cluster. Confirmed by reading
`/usr/share/container-scripts/postgresql/common.sh`. So rollback paths differ
between mid-upgrade failure and post-upgrade failure.

### If 06/08/10 exits non-zero (pg_upgrade failed mid-run)

SCL's error handler removes the partial new data dir (`rm -rf $PGDATA_new`).
The old data dir is still at `$PGDATA` untouched. Recovery:

1. `oc set env dc/postgresql POSTGRESQL_UPGRADE- -n uknscr-production`
2. `oc set triggers` to remove the failed target tag and restore the source tag
   (e.g. revert trigger to `openshift/postgresql:12-el8`)
3. `oc rollout latest dc/postgresql -n uknscr-production`
4. New pod comes up on source version with intact data dir. Zero data loss.

### If a verify step (07/09/11) fails OR app regression discovered after rollout

pg_upgrade already ran successfully so the old data dir is gone. Path:

1. `./scripts/prod-upgrade/01-scale-down.sh uknscr-production` (app down again)
2. Scale postgresql DC to 0, delete its PVC, recreate an empty PVC of the
   same size + storage class (ArgoCD manifest or manual apply).
3. Revert DC trigger to the source version (`openshift/postgresql:12-el8`).
4. Scale postgresql DC to 1 -> fresh empty PG 12 pod.
5. Restore the dump taken by 03-manual-backup.sh using the
   `restore_helper.py` module (spin a helper pod with PGHOST=postgresql,
   the dev namespace's postgresql secret, the prod backups bucket creds,
   and `DUMP_KEY=<name of the step-03 dump>`).
6. `./scripts/prod-upgrade/12-scale-up.sh uknscr-production`
7. Verify app loads.

Data loss window = 0 because 03-manual-backup.sh ran after 01-scale-down
+ 02-wait-for-quiet, so no writes happened between the backup and now.

### Catastrophic PVC corruption

If `05-snapshot-pv.sh` succeeded (VolumeSnapshot available), revert the
PVC from the snapshot; otherwise fall back to the dump-restore path above.

## Known risks

- TODO (flesh out from Fri's staging experience)

## Post-upgrade cleanup

- Revert `uknscr-k8s/build/postgresql-backup.yaml` BuildConfig ref back to `feat/backup-image` (or current default).
- Drop VolumeSnapshot after 7 days if no issues surface.
- Keep the step-03 dump in the bucket (90-day lifecycle will age it out).
