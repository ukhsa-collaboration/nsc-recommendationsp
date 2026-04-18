#!/usr/bin/env python3
"""Apply the backups-bucket lifecycle rule against the cluster-local NooBaa gateway.

Runs as a one-shot Kubernetes Job via an ArgoCD PostSync hook. Idempotent -
put_bucket_lifecycle_configuration overwrites any existing rules.
"""

from __future__ import annotations

import logging
import os
import sys

import boto3
import urllib3
from botocore.config import Config

# See deploy/backup.py for the rationale on verify=False.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
log = logging.getLogger("apply-lifecycle")


def main() -> None:
    try:
        bucket = os.environ["BUCKET_NAME"]
        access_key = os.environ["AWS_ACCESS_KEY_ID"]
        secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    except KeyError as missing:
        log.error("required env var %s is not set", missing.args[0])
        sys.exit(2)

    endpoint = os.environ.get("S3_ENDPOINT", "https://s3.openshift-storage.svc:443")
    retention_days = int(os.environ.get("RETENTION_DAYS", "90"))

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        verify=False,
        config=Config(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
    )

    rules = {
        "Rules": [
            {
                "ID": f"expire-backups-{retention_days}d",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "Expiration": {"Days": retention_days},
            }
        ]
    }

    s3.put_bucket_lifecycle_configuration(Bucket=bucket, LifecycleConfiguration=rules)
    applied = s3.get_bucket_lifecycle_configuration(Bucket=bucket)
    for rule in applied.get("Rules", []):
        log.info("applied: %s", rule)


if __name__ == "__main__":
    main()
