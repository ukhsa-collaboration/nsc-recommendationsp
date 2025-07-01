from urllib.parse import urlparse
import logging
from django.http import HttpResponseRedirect

logger = logging.getLogger(__name__)


def redirect_url_fragment(get_response):
    """
    Middleware that logs request headers and sets URL fragment on redirects
    """

    def middleware(request):
        headers_to_log = [
            "HTTP_X_FORWARDED_FOR",
            "HTTP_X_REAL_IP",
            "REMOTE_ADDR",
            "HTTP_USER_AGENT",
            "HTTP_CLIENT_IP",
            "HTTP_X_FORWARDED_HOST",
            "HTTP_X_FORWARDED_PROTO",
            "HTTP_FORWARDED",
            "HTTP_VIA",
            "HTTP_COOKIE",
        ]

        log_data = {
            header: request.META.get(header)
            for header in headers_to_log
            if header in request.META
        }

        request_url = request.build_absolute_uri()
        logger.info(f"[HeaderDebug] URL: {request_url} | Headers: {log_data}")

        response = get_response(request)

        if (
            isinstance(response, HttpResponseRedirect)
            and not urlparse(response.url).fragment
        ):
            return HttpResponseRedirect(f"{response.url}#")

        return response

    return middleware
