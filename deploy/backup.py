#!/usr/bin/env python3
"""Dump PostgreSQL and upload the archive to the cluster-local NooBaa S3 gateway.

Intended to run as a Kubernetes CronJob. Credentials come from env vars:

    PGUSER, PGPASSWORD, PGDATABASE, PGHOST (default "postgresql"), PGPORT (default "5432")
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME
    S3_ENDPOINT (default "https://s3.openshift-storage.svc:443")
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
from datetime import datetime, timezone

import boto3
import urllib3
from botocore.config import Config
from botocore.exceptions import ClientError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
log = logging.getLogger("backup")


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

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    key = f"uknscr-{timestamp}.dump"

    log.info(
        "pg_dump %s@%s:%s/%s -> s3://%s/%s (endpoint=%s)",
        pg_user, pg_host, pg_port, pg_database, bucket, key, endpoint,
    )

    s3 = build_s3_client(endpoint, access_key, secret_key)

    pg_dump_cmd = [
        "pg_dump",
        "-h", pg_host,
        "-p", pg_port,
        "-U", pg_user,
        "-d", pg_database,
        "-Fc",
        "--no-owner",
        "--no-privileges",
    ]

    proc_env = {**os.environ, "PGPASSWORD": pg_password}
    proc = subprocess.Popen(
        pg_dump_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=proc_env,
    )

    stderr_chunks: list[bytes] = []

    def drain_stderr() -> None:
        stream = proc.stderr
        if stream is None:
            return
        for chunk in iter(lambda: stream.read(4096), b""):
            stderr_chunks.append(chunk)

    stderr_thread = threading.Thread(target=drain_stderr, daemon=True)
    stderr_thread.start()

    try:
        s3.upload_fileobj(
            proc.stdout,
            bucket,
            key,
            ExtraArgs={"ContentType": "application/octet-stream"},
        )
    except ClientError:
        proc.kill()
        proc.wait()
        stderr_thread.join(timeout=5)
        log.exception("S3 upload failed; pg_dump stderr: %s", _decode(stderr_chunks))
        sys.exit(1)
    finally:
        if proc.stdout:
            proc.stdout.close()

    returncode = proc.wait()
    stderr_thread.join(timeout=5)
    stderr_text = _decode(stderr_chunks)

    if returncode != 0:
        log.error("pg_dump exited %s: %s", returncode, stderr_text.strip())
        _delete_partial(s3, bucket, key)
        sys.exit(1)

    if stderr_text.strip():
        log.info("pg_dump stderr: %s", stderr_text.strip())

    try:
        head = s3.head_object(Bucket=bucket, Key=key)
    except ClientError:
        log.exception("head_object failed post-upload")
        sys.exit(1)

    size = head["ContentLength"]
    if size == 0:
        log.error("uploaded object is 0 bytes; deleting")
        _delete_partial(s3, bucket, key)
        sys.exit(1)

    log.info("backup complete: s3://%s/%s (%s bytes)", bucket, key, size)


def _decode(chunks: list[bytes]) -> str:
    return b"".join(chunks).decode("utf-8", errors="replace")


def _delete_partial(s3, bucket: str, key: str) -> None:
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        log.info("deleted partial upload s3://%s/%s", bucket, key)
    except ClientError:
        log.warning("failed to delete partial upload s3://%s/%s", bucket, key)


if __name__ == "__main__":
    main()
