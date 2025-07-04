"""
nsc.utils.virus_scanner
----------------------

Thin wrapper around ClamAV (`clamd` Python binding).
"""
from __future__ import annotations

import io
import logging
import os
from functools import lru_cache
from typing import BinaryIO

import clamd
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)

CLAMD_HOST = os.getenv("CLAMAV_HOST", "clamav")
CLAMD_PORT = int(os.getenv("CLAMAV_PORT", 3310))


# ────────────────────────────────────────────────────────────────────────────────
# Connection helper
# ────────────────────────────────────────────────────────────────────────────────
@lru_cache
def _get_client() -> clamd.ClamdNetworkSocket:
    """
    Return a singleton Clamd client connected to the network daemon.

    Raises
    ------
    clamd.ConnectionError
        If the daemon is unreachable.
    """
    logger.debug("Connecting to ClamAV daemon at %s:%s …", CLAMD_HOST, CLAMD_PORT)
    cd = clamd.ClamdNetworkSocket(host=CLAMD_HOST, port=CLAMD_PORT)
    cd.ping()  # Fail fast if clamd isn't ready
    logger.debug("Successfully connected to ClamAV")
    return cd


# ────────────────────────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────────────────────────
def is_file_clean(django_file: UploadedFile | BinaryIO) -> bool:
    """
    Scan a Django ``UploadedFile`` (or any file‑like object) for malware.

    Returns
    -------
    bool
        ``True`` if the file is clean, ``False`` otherwise.

    Notes
    -----
    *   If the file has a real path on disk (`TemporaryUploadedFile`) we use
        the fast ``SCAN`` command.
    *   Otherwise we fall back to ``INSTREAM`` to avoid writing the file out.
    *   We always restore the file pointer, so the caller can continue reading.
    """
    try:
        client = _get_client()

        # ── 1. Large uploads already on disk → use .scan(path) ──────────────
        if hasattr(django_file, "temporary_file_path"):  # TemporaryUploadedFile
            file_path = django_file.temporary_file_path()
            logger.debug("Scanning via SCAN %s", file_path)
            scan_result = client.scan(file_path)  # {'/tmp/abc': ('OK', None)}
            status, sig = scan_result.get(file_path, ("UNKNOWN", None))

        # ── 2. In‑memory uploads → stream bytes to clamd ────────────────────
        else:
            # Ensure we stream from the beginning, then restore the pointer
            pos = django_file.tell() if hasattr(django_file, "tell") else 0
            if hasattr(django_file, "seek"):
                django_file.seek(0)

            logger.debug("Scanning via INSTREAM (%s bytes)", django_file.size)
            # clamd expects a file‑like object; wrap bytes IO if needed
            fh: BinaryIO = (
                django_file
                if hasattr(django_file, "read")
                else io.BytesIO(django_file)  # type: ignore[arg-type]
            )
            scan_result = client.instream(fh)  # {'stream': ('OK', None)}
            status, sig = scan_result.get("stream", ("UNKNOWN", None))

            if hasattr(django_file, "seek"):
                django_file.seek(pos)

        logger.info("ClamAV result: %s %s", status, sig or "")
        return status == "OK"

    except Exception as exc:  # noqa: BLE001
        logger.error("ClamAV scan failed: %s", exc, exc_info=True)
        # Fail closed – treat any error the same as 'infected'
        return False
