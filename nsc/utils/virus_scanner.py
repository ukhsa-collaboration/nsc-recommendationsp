import logging
from typing import BinaryIO

from django.conf import settings

import clamd


logger = logging.getLogger("nsc.utils.virus_scanner")
logger.debug("Virus scanner module imported")


def is_file_clean(file: BinaryIO) -> bool:
    """
    Scan *file* with ClamAV. Return True iff the status is “OK”.
    On any connection/streaming error we **fail‑open** and return True.
    """
    logger.debug("Entered is_file_clean")

    file.seek(0)  # rewind before streaming

    try:
        cd = clamd.ClamdNetworkSocket(
            host=settings.CLAMAV_HOST,
            port=settings.CLAMAV_PORT,
            timeout=settings.CLAMAV_TIMEOUT,
        )
    except Exception as exc:
        logger.warning("Could not connect to clamd: %s – allowing upload", exc)
        return True  # fail‑open on connection error

    try:
        result = cd.instream(file)
    except Exception as exc:
        logger.warning("Error while streaming file to clamd: %s – allowing upload", exc)
        return True  # fail‑open on streaming error
    finally:
        file.seek(0)  # let callers read again

    status, _sig = result.get("stream", ("ERROR", None))
    return status == "OK"
