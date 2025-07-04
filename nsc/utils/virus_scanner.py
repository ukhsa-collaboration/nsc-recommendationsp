import logging
from typing import BinaryIO

import clamd


logger = logging.getLogger("nsc.utils.virus_scanner")
logger.debug("Virus scanner module imported")


def is_file_clean(file: BinaryIO) -> bool:
    """
    Scan *file* with ClamAV and return True only if the result is “OK”.

    Parameters
    ----------
    file : BinaryIO
        A Django File (or any object with .seek() and .chunks()).

    Returns
    -------
    bool
        • True  – no virus found (“OK”)
        • False – signature found OR scan could not be completed
    """
    logger.debug("Entered is_file_clean")

    # Always rewind so we stream the entire content
    file.seek(0)

    try:
        cd = clamd.ClamdNetworkSocket(host="clamav", port=3310, timeout=10)
    except Exception as exc:
        logger.error("Could not connect to clamd: %s", exc, exc_info=True)
        return False  # fail closed

    try:
        result = cd.instream(file)
        logger.debug("ClamAV scan result: %s", result)
    except Exception as exc:
        logger.error("Error while streaming file to clamd: %s", exc, exc_info=True)
        return False  # fail closed
    finally:
        # Let callers read the file again if they need to
        file.seek(0)

    status, _sig = result.get("stream", ("ERROR", None))
    return status == "OK"
