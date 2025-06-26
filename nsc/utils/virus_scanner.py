import logging

import clamd


logger = logging.getLogger(__name__)


def is_file_clean(file):
    """
    Returns True if clean or scan fails (fail-open).
    Returns False only if ClamAV definitively reports malware.
    """
    try:
        cd = clamd.ClamdUnixSocket()
    except Exception as e:
        logger.warning(f"Error connecting to clamd: {e}")
        return True  # ⚠️ Fail open (don't block upload)

    file.seek(0)
    try:
        result = cd.instream(file)
        status, _ = result.get("stream", ("ERROR", None))
        return status == "OK"
    except Exception as e:
        logger.warning(f"Error scanning file: {e}")
        return True  # ⚠️ Fail open
