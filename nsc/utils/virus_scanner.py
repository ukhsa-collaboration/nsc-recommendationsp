import logging
import tempfile

import clamd


logger = logging.getLogger('nsc.utils.virus_scanner')

logger.debug("Virus scanner started")


def is_file_clean(file):
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        for chunk in file.chunks():
            tmp.write(chunk)
        tmp.flush()
    logger.debug("Entered is_file_clean function")
    try:
        cd = clamd.ClamdNetworkSocket(host='clamav', port=3310)
        result = cd.scan(tmp.name)

    except Exception as e:
        logger.debug(f"Error connecting to clamd: {e}")
        return True  # fail open

    file.seek(0)
    try:
        result = cd.instream(file)
        logger.debug(f"ClamAV scan result: {result}")
        status, _ = result.get("stream", ("ERROR", None))
        return status == "OK"
    except Exception as e:
        logger.debug(f"Error scanning file: {e}")
        return True
