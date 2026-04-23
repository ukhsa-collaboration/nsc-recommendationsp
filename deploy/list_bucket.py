#!/usr/bin/env python3
"""List objects in the backups S3 bucket with totals and lifecycle info.

Reads AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME from env.
Optional: S3_ENDPOINT (default https://s3.openshift-storage.svc:443).

Intended to run inside a pod against the NooBaa internal S3 gateway.
See deploy/backup.py for the upload-side of this same client config.
"""

from __future__ import annotations

import os
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"required env var {name} is not set", file=sys.stderr)
        sys.exit(2)
    return value


def main() -> None:
    bucket = require_env("BUCKET_NAME")
    access_key = require_env("AWS_ACCESS_KEY_ID")
    secret_key = require_env("AWS_SECRET_ACCESS_KEY")
    endpoint = os.environ.get("S3_ENDPOINT", "https://s3.openshift-storage.svc:443")

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

    print(f"bucket: {bucket}")
    print()

    total = 0
    count = 0
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            print(f"{obj['LastModified'].isoformat()}  {obj['Size']:>12}  {obj['Key']}")
            total += obj["Size"]
            count += 1
    print()
    print(f"{count} objects, {total} bytes total")
    print()

    try:
        lc = s3.get_bucket_lifecycle_configuration(Bucket=bucket)
        print("Lifecycle rules:")
        for rule in lc.get("Rules", []):
            days = rule.get("Expiration", {}).get("Days", "-")
            print(f"  {rule.get('ID')}  expire={days}d  status={rule.get('Status')}")
    except ClientError as e:
        code = e.response["Error"].get("Code", "?")
        print(f"Lifecycle: none configured ({code})")


if __name__ == "__main__":
    main()
