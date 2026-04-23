# Prod PG 12 -> 15 Upgrade Runbook

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

*Purpose:* Same as step 07 but at the final version.
*Script:* `./scripts/prod-upgrade/09-verify-pg15.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

### 10 - Scale back up

*Purpose:* django-webpack, celery-worker, celery-beat back to replica counts. Maintenance page off.
*Script:* `./scripts/prod-upgrade/10-scale-up.sh uknscr-production`
*Proceed if:* TODO
*Stop if:* TODO

## Rollback

*Script:* `./scripts/prod-upgrade/99-rollback.sh uknscr-production`

TODO: expand after staging rehearsal on Fri. Plan A is VolumeSnapshot restore;
Plan B is restore from the step-03 dump into a fresh PV; Plan C is pointing
the DeploymentConfig back to the old image tag (works only if step 06's
POSTGRESQL_UPGRADE=copy hasn't overwritten the on-disk data dir).

## Known risks

- TODO (flesh out from Fri's staging experience)

## Post-upgrade cleanup

- Revert `uknscr-k8s/build/postgresql-backup.yaml` BuildConfig ref back to `feat/backup-image` (or current default).
- Drop VolumeSnapshot after 7 days if no issues surface.
- Keep the step-03 dump in the bucket (90-day lifecycle will age it out).
