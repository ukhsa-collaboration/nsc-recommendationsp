"""
Global context processors
"""
import logging
import socket

from django.conf import settings

logger = logging.getLogger(__name__)


def webpack_dev_url(request):
    """
    If webpack dev server is running, add HMR context processor so template can
    switch script import to HMR URL
    """
    if settings.WEBPACK_DEV_URL is None:
        return {}

    hmr_socket = socket.socket()
    try:
        hmr_socket.connect(
            (settings.WEBPACK_DEV_HOST, settings.WEBPACK_DEV_PORT),
        )

    except socket.error:
        # No HMR server
        logger.warning('Webpack dev server not found\n')
        return {}

    finally:
        hmr_socket.close()

    # HMR server found
    logger.info('Webpack dev server found, HMR enabled\n')

    return {
        'WEBPACK_DEV_URL': settings.WEBPACK_DEV_URL,
    }
