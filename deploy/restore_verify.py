#!/usr/bin/env python3
"""Emit a verifiable summary of a PostgreSQL database for upgrade/restore drills.

Prints to stdout in the same shape that 00-preflight.sh snapshots:

    pg_version=<server_version>

    ## row counts (pg_stat_user_tables)
    <schema>\t<relname>\t<n_live_tup>
    ...

    ## schema hash (sha256 of pg_dump -s)
    <sha256>  -

The caller (07-verify-pg13.sh / 09-verify-pg15.sh / 11-verify-pg16.sh and
04-restore-drill.sh) diffs this against the preflight baseline. Row counts
should be stable across upgrades; the schema hash only matches on
same-major-version restores because pg_dump emits version-specific DDL.

Env vars (each accepts either a PG* or POSTGRESQL_* variant):
    PGUSER     | POSTGRESQL_USER       required
    PGPASSWORD | POSTGRESQL_PASSWORD   required
    PGDATABASE | POSTGRESQL_DATABASE   required
    PGHOST                             optional, default "" (socket)
    PGPORT                             optional, default "5432"

Exit codes:
    0 on success
    2 if required env is missing
    1 if psql/pg_dump fails
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys


def _env(*names: str) -> str:
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    print(f"missing required env: one of {names}", file=sys.stderr)
    sys.exit(2)


def _psql(env: dict[str, str], sql: str) -> str:
    proc = subprocess.run(
        ["psql", "-tAF", "\t", "-v", "ON_ERROR_STOP=1", "-c", sql],
        capture_output=True,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode(errors="replace"))
        sys.exit(1)
    return proc.stdout.decode()


def main() -> int:
    env = dict(os.environ)
    env["PGUSER"] = _env("PGUSER", "POSTGRESQL_USER")
    env["PGPASSWORD"] = _env("PGPASSWORD", "POSTGRESQL_PASSWORD")
    env["PGDATABASE"] = _env("PGDATABASE", "POSTGRESQL_DATABASE")
    env.setdefault("PGHOST", os.environ.get("PGHOST", ""))
    env.setdefault("PGPORT", os.environ.get("PGPORT", "5432"))

    version = _psql(env, "SHOW server_version;").strip()
    print(f"pg_version={version}")
    print()
    # Exact COUNT(*) per user table. pg_stat_user_tables.n_live_tup is a
    # statistic populated by ANALYZE; it reads 0 for every table right after
    # pg_upgrade/pg_restore until autovacuum catches up, which makes
    # cross-hop diffs meaningless. A single-scan SELECT count(*) is fine
    # for uknscr-sized DBs (~3.3 MB in prod).
    print("## row counts (exact COUNT(*))")
    tables_raw = _psql(
        env,
        "SELECT schemaname, relname FROM pg_stat_user_tables "
        "WHERE schemaname NOT IN ('pg_catalog','information_schema') "
        "ORDER BY 1, 2;",
    )
    for line in tables_raw.splitlines():
        if not line.strip():
            continue
        schema, table = line.split("\t", 1)
        count = _psql(
            env,
            # quote_ident() handles mixed-case / reserved-word identifiers.
            f'SELECT count(*) FROM "{schema}"."{table}";',
        ).strip()
        print(f"{schema}\t{table}\t{count}")
    print()
    print("## schema hash (sha256 of pg_dump -s)")

    dump = subprocess.run(
        ["pg_dump", "-s", "--no-owner", "--no-acl"],
        capture_output=True,
        env=env,
        check=False,
    )
    if dump.returncode != 0:
        sys.stderr.write(dump.stderr.decode(errors="replace"))
        return 1
    digest = hashlib.sha256(dump.stdout).hexdigest()
    print(f"{digest}  -")
    return 0


if __name__ == "__main__":
    sys.exit(main())
