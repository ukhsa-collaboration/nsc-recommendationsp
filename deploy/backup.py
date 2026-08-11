#!/usr/bin/env python3
"""Dump PostgreSQL and upload the archive to the cluster-local NooBaa S3 gateway.

Intended to run as a Kubernetes CronJob. Credentials come from env vars:

    PGUSER, PGPASSWORD, PGDATABASE, PGHOST (default "postgresql"), PGPORT (default "5432")
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME
    S3_ENDPOINT (default "https://s3.openshift-storage.svc:443")
    RETENTION_DAYS (default "90") - in-job prune of objects older than this
    WORK_DIR (default "/tmp/backup") - staging directory for the dump file
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
import os
from pathlib import Path
import subprocess
import sys
import threading

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import urllib3


# Internal NooBaa endpoint uses a self-signed cert served only within the cluster.
# Traffic is gated by the allow-openshift-storage NetworkPolicy so the path is
# authenticated at the network layer. Do NOT copy this pattern into code that
# talks to public S3 - always verify TLS there.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
log = logging.getLogger("backup")

MAX_STDERR_BYTES = 1 * 1024 * 1024
PG_DUMP_MAGIC = b"PGDMP"
DEFAULT_RETENTION_DAYS = 90


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        log.error("required env var %s is not set", name)
        sys.exit(2)
    return value


def get_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError:
        log.error("STEP_01_CONFIG invalid integer for %s: %r", name, raw)
        sys.exit(2)
    if value < 0:
        log.error("STEP_01_CONFIG %s must be >= 0, got %s", name, value)
        sys.exit(2)
    return value


def build_s3_client(endpoint: str, access_key: str, secret_key: str):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        verify=False,
        config=Config(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )


def main() -> None:
    log.info("STEP_00_START backup job starting")

    pg_user = require_env("PGUSER")
    pg_password = require_env("PGPASSWORD")
    pg_database = require_env("PGDATABASE")
    pg_host = os.environ.get("PGHOST", "postgresql")
    pg_port = os.environ.get("PGPORT", "5432")

    bucket = require_env("BUCKET_NAME")
    access_key = require_env("AWS_ACCESS_KEY_ID")
    secret_key = require_env("AWS_SECRET_ACCESS_KEY")
    endpoint = os.environ.get("S3_ENDPOINT", "https://s3.openshift-storage.svc:443")

    retention_days = get_int_env("RETENTION_DAYS", DEFAULT_RETENTION_DAYS)
    work_dir = Path(os.environ.get("WORK_DIR", "/tmp/backup"))
    work_dir.mkdir(parents=True, exist_ok=True)

    log.info(
        "STEP_01_CONFIG runtime config: pg_host=%s pg_port=%s pg_database=%s bucket=%s endpoint=%s retention_days=%s work_dir=%s",
        pg_host,
        pg_port,
        pg_database,
        bucket,
        endpoint,
        retention_days,
        work_dir,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    key = f"uknscr-{timestamp}.dump"
    dump_path = work_dir / key

    log.info("STEP_02_PREP generated backup key: %s", key)

    log.info(
        "STEP_03_DUMP pg_dump %s@%s:%s/%s -> %s",
        pg_user,
        pg_host,
        pg_port,
        pg_database,
        dump_path,
    )

    run_pg_dump(
        pg_host=pg_host,
        pg_port=pg_port,
        pg_user=pg_user,
        pg_password=pg_password,
        pg_database=pg_database,
        dump_path=dump_path,
    )

    log.info("STEP_04_LOCAL_VALIDATE pg_dump command completed, validating local artifact")

    dump_size = dump_path.stat().st_size
    if dump_size == 0:
        log.error("STEP_04_LOCAL_VALIDATE pg_dump produced a 0-byte file")
        dump_path.unlink(missing_ok=True)
        sys.exit(1)

    with dump_path.open("rb") as f:
        local_magic = f.read(len(PG_DUMP_MAGIC))
    if local_magic != PG_DUMP_MAGIC:
        log.error(
            "STEP_04_LOCAL_VALIDATE pg_dump output does not start with PGDMP magic: got %r",
            local_magic,
        )
        dump_path.unlink(missing_ok=True)
        sys.exit(1)

    log.info(
        "STEP_04_LOCAL_VALIDATE pg_dump complete: %s bytes, PGDMP magic verified locally",
        dump_size,
    )

    log.info("STEP_05_UPLOAD creating S3 client for endpoint %s", endpoint)
    s3 = build_s3_client(endpoint, access_key, secret_key)
    log.info("STEP_05_UPLOAD uploading to s3://%s/%s", bucket, key)
    try:
        s3.upload_file(
            str(dump_path),
            bucket,
            key,
            ExtraArgs={"ContentType": "application/octet-stream"},
        )
    except ClientError:
        log.exception("STEP_05_UPLOAD S3 upload failed")
        sys.exit(1)
    finally:
        dump_path.unlink(missing_ok=True)
        log.info("STEP_05_UPLOAD cleaned up local dump file %s", dump_path)

    log.info("STEP_06_REMOTE_VALIDATE upload complete, validating remote object metadata")
    try:
        head = s3.head_object(Bucket=bucket, Key=key)
    except ClientError:
        log.exception("STEP_06_REMOTE_VALIDATE head_object failed post-upload")
        sys.exit(1)

    remote_size = head["ContentLength"]
    if remote_size != dump_size:
        log.error(
            "STEP_06_REMOTE_VALIDATE uploaded size %s != local size %s",
            remote_size,
            dump_size,
        )
        delete_key(s3, bucket, key)
        sys.exit(1)

    log.info("STEP_06_REMOTE_VALIDATE remote size validation passed: %s bytes", remote_size)

    try:
        resp = s3.get_object(
            Bucket=bucket,
            Key=key,
            Range=f"bytes=0-{len(PG_DUMP_MAGIC) - 1}",
        )
        remote_magic = resp["Body"].read()
    except ClientError:
        log.exception("STEP_06_REMOTE_VALIDATE range-get of uploaded object failed")
        sys.exit(1)

    if remote_magic != PG_DUMP_MAGIC:
        log.error(
            "STEP_06_REMOTE_VALIDATE uploaded object magic %r != expected %r",
            remote_magic,
            PG_DUMP_MAGIC,
        )
        delete_key(s3, bucket, key)
        sys.exit(1)

    log.info("STEP_06_REMOTE_VALIDATE remote magic validation passed")

    log.info(
        "STEP_07_VERIFIED backup verified: s3://%s/%s (%s bytes)",
        bucket,
        key,
        remote_size,
    )

    log.info("STEP_08_PRUNE starting retention prune")
    prune_old_backups(s3, bucket, retention_days)
    log.info("STEP_09_DONE backup job completed successfully")


def run_pg_dump(
    *,
    pg_host: str,
    pg_port: str,
    pg_user: str,
    pg_password: str,
    pg_database: str,
    dump_path: Path,
) -> None:
    log.info("STEP_03_DUMP starting pg_dump subprocess")
    cmd = [
        "pg_dump",
        "-h",
        pg_host,
        "-p",
        pg_port,
        "-U",
        pg_user,
        "-d",
        pg_database,
        "-Fc",
        "-Z",
        "9",
        "--no-owner",
        "--no-privileges",
        "--file",
        str(dump_path),
    ]
    log.info("STEP_03_DUMP pg_dump command args: %s", " ".join(cmd))
    proc_env = {**os.environ, "PGPASSWORD": pg_password}
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, env=proc_env)

    stderr_buf = bytearray()
    truncated = False

    def drain_stderr() -> None:
        nonlocal truncated
        stream = proc.stderr
        if stream is None:
            return
        for chunk in iter(lambda: stream.read(4096), b""):
            remaining = MAX_STDERR_BYTES - len(stderr_buf)
            if remaining <= 0:
                truncated = True
                break
            stderr_buf.extend(chunk[:remaining])

    t = threading.Thread(target=drain_stderr, daemon=True)
    t.start()
    log.info("STEP_03_DUMP waiting for pg_dump process to complete")
    returncode = proc.wait()
    t.join(timeout=5)
    log.info("STEP_03_DUMP pg_dump process finished with return code %s", returncode)

    stderr_text = stderr_buf.decode("utf-8", errors="replace")
    if truncated:
        stderr_text += "\n...[stderr truncated at 1 MiB]"

    if returncode != 0:
        log.error("STEP_03_DUMP pg_dump exited %s: %s", returncode, stderr_text.strip())
        dump_path.unlink(missing_ok=True)
        sys.exit(1)

    if stderr_text.strip():
        log.info("STEP_03_DUMP pg_dump stderr (warnings): %s", stderr_text.strip())


def prune_old_backups(s3, bucket: str, retention_days: int) -> None:
    log.info(
        "STEP_08_PRUNE prune scan starting for bucket=%s retention_days=%s",
        bucket,
        retention_days,
    )
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    deleted = 0
    scanned = 0
    pages = 0
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix="uknscr-"):
        pages += 1
        page_contents = page.get("Contents", [])
        scanned += len(page_contents)
        log.info("STEP_08_PRUNE prune page %s: %s object(s)", pages, len(page_contents))
        for obj in page_contents:
            if obj["LastModified"] < cutoff:
                try:
                    s3.delete_object(Bucket=bucket, Key=obj["Key"])
                    log.info(
                        "STEP_08_PRUNE pruned old backup s3://%s/%s (age=%s)",
                        bucket,
                        obj["Key"],
                        datetime.now(timezone.utc) - obj["LastModified"],
                    )
                    deleted += 1
                except ClientError:
                    log.warning("STEP_08_PRUNE failed to prune s3://%s/%s", bucket, obj["Key"])
    log.info(
        "STEP_08_PRUNE prune scan complete: pages=%s scanned=%s deleted=%s",
        pages,
        scanned,
        deleted,
    )
    if deleted:
        log.info(
            "STEP_08_PRUNE pruned %s backup(s) older than %s days",
            deleted,
            retention_days,
        )


def delete_key(s3, bucket: str, key: str) -> None:
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        log.info("STEP_06_REMOTE_VALIDATE deleted bad upload s3://%s/%s", bucket, key)
    except ClientError:
        log.warning("STEP_06_REMOTE_VALIDATE failed to delete bad upload s3://%s/%s", bucket, key)


if __name__ == "__main__":
    main()
