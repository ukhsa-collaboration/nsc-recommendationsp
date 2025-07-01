from urllib.parse import urlparse
import logging
from django.http import HttpResponseRedirect

logger = logging.getLogger(__name__)


def redirect_url_fragment(get_response):
    """
    Middleware that logs request headers and sets URL fragment on redirects
    """

    def middleware(request):
        response = get_response(request)

        if (
            isinstance(response, HttpResponseRedirect)
            and not urlparse(response.url).fragment
        ):
            return HttpResponseRedirect(f"{response.url}#")

        return response

    return middleware
