import logging

logger = logging.getLogger(__name__)


class HeaderDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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

        logger.info(f"[HeaderDebug] {log_data}")

        return self.get_response(request)