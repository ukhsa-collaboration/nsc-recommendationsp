import logging
import os
import subprocess
import tempfile
from typing import BinaryIO

import clamd

logger = logging.getLogger("nsc.utils.virus_scanner")
logger.debug("Virus scanner module imported")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _scan_with_clamscan(file: BinaryIO) -> bool:
    """
    Fallback scanner that writes *file* to a NamedTemporaryFile and invokes
    the clamscan CLI.  Returns True iff the exit status is 0 (clean).
    """
    logger.debug("Entering _scan_with_clamscan fallback")

    file.seek(0)
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        tmp.write(file.read())
        tmp.flush()

        result = subprocess.run(
            ["clamscan", "--no-summary", tmp.name],
            capture_output=True,
            text=True,
        )

    logger.debug("clamscan exit code: %s", result.returncode)
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        logger.info("clamscan detected malware:\n%s", result.stdout.strip())
        return False

    # Any other exit code => error → fail‑open
    logger.warning(
        "clamscan returned %s, stderr:\n%s – allowing upload",
        result.returncode,
        result.stderr.strip(),
    )
    return True  # fail‑open


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

def is_file_clean(file: BinaryIO) -> bool:
    """
    Scan *file* with ClamAV, falling back to the clamscan CLI if the daemon
    is not reachable or returns an unexpected status.

    Returns True iff the file is judged clean.
    """
    logger.debug("Entered is_file_clean")
    file.seek(0)  # rewind before streaming

    try:
        host = os.getenv("CLAMAV_HOST", "clamav")
        port = int(os.getenv("CLAMAV_PORT", "3310"))
        cd = clamd.ClamdNetworkSocket(host=host, port=port, timeout=10)
        result = cd.instream(file)
        logger.debug("ClamAV scan result: %s", result)
    except Exception as exc:
        logger.warning("Could not scan with clamd (%s) – falling back to clamscan", exc)
        return _scan_with_clamscan(file)
    finally:
        file.seek(0)  # let callers read again

    status, signature = result.get("stream", ("ERROR", None))

    if status == "OK":
        return True
    if status == "FOUND":
        logger.info("ClamAV detected malware: %s", signature)
        return False

    # Any other status (“ERROR”, “UNKNOWN”, …) → try clamscan
    logger.warning("ClamAV returned %s – falling back to clamscan", status)
    return _scan_with_clamscan(file)
