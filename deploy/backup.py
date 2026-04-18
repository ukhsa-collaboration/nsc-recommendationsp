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
    pg_user = require_env("PGUSER")
    pg_password = require_env("PGPASSWORD")
    pg_database = require_env("PGDATABASE")
    pg_host = os.environ.get("PGHOST", "postgresql")
    pg_port = os.environ.get("PGPORT", "5432")

    bucket = require_env("BUCKET_NAME")
    access_key = require_env("AWS_ACCESS_KEY_ID")
    secret_key = require_env("AWS_SECRET_ACCESS_KEY")
    endpoint = os.environ.get("S3_ENDPOINT", "https://s3.openshift-storage.svc:443")

    retention_days = int(os.environ.get("RETENTION_DAYS", str(DEFAULT_RETENTION_DAYS)))
    work_dir = Path(os.environ.get("WORK_DIR", "/tmp/backup"))
    work_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    key = f"uknscr-{timestamp}.dump"
    dump_path = work_dir / key

    log.info(
        "pg_dump %s@%s:%s/%s -> %s",
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

    dump_size = dump_path.stat().st_size
    if dump_size == 0:
        log.error("pg_dump produced a 0-byte file")
        dump_path.unlink(missing_ok=True)
        sys.exit(1)

    with dump_path.open("rb") as f:
        local_magic = f.read(len(PG_DUMP_MAGIC))
    if local_magic != PG_DUMP_MAGIC:
        log.error("pg_dump output does not start with PGDMP magic: got %r", local_magic)
        dump_path.unlink(missing_ok=True)
        sys.exit(1)

    log.info("pg_dump complete: %s bytes, PGDMP magic verified locally", dump_size)

    s3 = build_s3_client(endpoint, access_key, secret_key)
    log.info("uploading to s3://%s/%s", bucket, key)
    try:
        s3.upload_file(
            str(dump_path),
            bucket,
            key,
            ExtraArgs={"ContentType": "application/octet-stream"},
        )
    except ClientError:
        log.exception("S3 upload failed")
        sys.exit(1)
    finally:
        dump_path.unlink(missing_ok=True)

    try:
        head = s3.head_object(Bucket=bucket, Key=key)
    except ClientError:
        log.exception("head_object failed post-upload")
        sys.exit(1)

    remote_size = head["ContentLength"]
    if remote_size != dump_size:
        log.error("uploaded size %s != local size %s", remote_size, dump_size)
        delete_key(s3, bucket, key)
        sys.exit(1)

    try:
        resp = s3.get_object(
            Bucket=bucket,
            Key=key,
            Range=f"bytes=0-{len(PG_DUMP_MAGIC) - 1}",
        )
        remote_magic = resp["Body"].read()
    except ClientError:
        log.exception("range-get of uploaded object failed")
        sys.exit(1)

    if remote_magic != PG_DUMP_MAGIC:
        log.error(
            "uploaded object magic %r != expected %r", remote_magic, PG_DUMP_MAGIC
        )
        delete_key(s3, bucket, key)
        sys.exit(1)

    log.info("backup verified: s3://%s/%s (%s bytes)", bucket, key, remote_size)

    prune_old_backups(s3, bucket, retention_days)


def run_pg_dump(
    *,
    pg_host: str,
    pg_port: str,
    pg_user: str,
    pg_password: str,
    pg_database: str,
    dump_path: Path,
) -> None:
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
    returncode = proc.wait()
    t.join(timeout=5)

    stderr_text = stderr_buf.decode("utf-8", errors="replace")
    if truncated:
        stderr_text += "\n...[stderr truncated at 1 MiB]"

    if returncode != 0:
        log.error("pg_dump exited %s: %s", returncode, stderr_text.strip())
        dump_path.unlink(missing_ok=True)
        sys.exit(1)

    if stderr_text.strip():
        log.info("pg_dump stderr (warnings): %s", stderr_text.strip())


def prune_old_backups(s3, bucket: str, retention_days: int) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    deleted = 0
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix="uknscr-"):
        for obj in page.get("Contents", []):
            if obj["LastModified"] < cutoff:
                try:
                    s3.delete_object(Bucket=bucket, Key=obj["Key"])
                    log.info(
                        "pruned old backup s3://%s/%s (age=%s)",
                        bucket,
                        obj["Key"],
                        datetime.now(timezone.utc) - obj["LastModified"],
                    )
                    deleted += 1
                except ClientError:
                    log.warning("failed to prune s3://%s/%s", bucket, obj["Key"])
    if deleted:
        log.info("pruned %s backup(s) older than %s days", deleted, retention_days)


def delete_key(s3, bucket: str, key: str) -> None:
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        log.info("deleted bad upload s3://%s/%s", bucket, key)
    except ClientError:
        log.warning("failed to delete bad upload s3://%s/%s", bucket, key)


if __name__ == "__main__":
    main()
