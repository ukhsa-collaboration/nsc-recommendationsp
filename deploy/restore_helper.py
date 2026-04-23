#!/usr/bin/env python3
"""Fetch the most recent .dump from the backups bucket and pg_restore it into
the local PG server. Mirror of deploy/backup.py's upload direction.

Intended for the restore drill (scripts/prod-upgrade/04-restore-drill.sh):
a throwaway PG pod is started from the postgresql-backup image with the SCL
entrypoint (so it runs a PG server on localhost), this module fetches the
latest dump from S3, and pg_restore replays it into the local drill DB.

Env vars (required):
    PGUSER, PGPASSWORD, PGDATABASE     target DB (restored schema+data goes here)
    BUCKET_NAME                        source bucket
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
Optional:
    PGHOST (default "localhost"), PGPORT (default "5432")
    S3_ENDPOINT (default "https://s3.openshift-storage.svc:443")
    WORK_DIR (default "/tmp/restore")
    DUMP_KEY                           override; otherwise picks most recent
                                       object matching uknscr-*.dump
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import subprocess
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
log = logging.getLogger("restore")

PG_DUMP_MAGIC = b"PGDMP"


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


def pick_latest_dump(s3, bucket: str) -> str:
    paginator = s3.get_paginator("list_objects_v2")
    latest_key = None
    latest_mtime = None
    for page in paginator.paginate(Bucket=bucket, Prefix="uknscr-"):
        for obj in page.get("Contents", []):
            if not obj["Key"].endswith(".dump"):
                continue
            if latest_mtime is None or obj["LastModified"] > latest_mtime:
                latest_mtime = obj["LastModified"]
                latest_key = obj["Key"]
    if not latest_key:
        log.error("no uknscr-*.dump found in bucket %s", bucket)
        sys.exit(1)
    return latest_key


def main() -> int:
    pg_user = require_env("PGUSER")
    pg_password = require_env("PGPASSWORD")
    pg_database = require_env("PGDATABASE")
    pg_host = os.environ.get("PGHOST", "localhost")
    pg_port = os.environ.get("PGPORT", "5432")

    bucket = require_env("BUCKET_NAME")
    access_key = require_env("AWS_ACCESS_KEY_ID")
    secret_key = require_env("AWS_SECRET_ACCESS_KEY")
    endpoint = os.environ.get("S3_ENDPOINT", "https://s3.openshift-storage.svc:443")

    work_dir = Path(os.environ.get("WORK_DIR", "/tmp/restore"))
    work_dir.mkdir(parents=True, exist_ok=True)

    s3 = build_s3_client(endpoint, access_key, secret_key)
    key = os.environ.get("DUMP_KEY") or pick_latest_dump(s3, bucket)
    local_path = work_dir / Path(key).name

    log.info("fetching s3://%s/%s -> %s", bucket, key, local_path)
    try:
        s3.download_file(bucket, key, str(local_path))
    except ClientError:
        log.exception("S3 download failed")
        return 1

    size = local_path.stat().st_size
    if size == 0:
        log.error("downloaded dump is 0 bytes")
        return 1

    with local_path.open("rb") as f:
        magic = f.read(len(PG_DUMP_MAGIC))
    if magic != PG_DUMP_MAGIC:
        log.error("downloaded file is not a pg_dump custom-format archive: %r", magic)
        return 1
    log.info("downloaded %d bytes, PGDMP magic verified", size)

    env = dict(os.environ)
    env["PGPASSWORD"] = pg_password
    cmd = [
        "pg_restore",
        "-h",
        pg_host,
        "-p",
        pg_port,
        "-U",
        pg_user,
        "-d",
        pg_database,
        "--clean",
        "--if-exists",
        "--no-owner",
        "--no-acl",
        str(local_path),
    ]
    log.info("pg_restore -> %s@%s:%s/%s", pg_user, pg_host, pg_port, pg_database)
    proc = subprocess.run(cmd, env=env, capture_output=True)
    if proc.returncode != 0:
        log.error(
            "pg_restore exited %d:\n%s",
            proc.returncode,
            proc.stderr.decode(errors="replace"),
        )
        return 1

    log.info("restore complete from s3://%s/%s (%d bytes)", bucket, key, size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
