import logging
from ipware import get_client_ip

logger = logging.getLogger(__name__)


class HeaderDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("✅ HeaderDebugMiddleware initialized.")

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

        # Extract standard headers
        log_data = {
            header: request.META.get(header)
            for header in headers_to_log
            if header in request.META
        }

        # Get client IP using ipware
        client_ip, is_routable = get_client_ip(request)
        log_data["client_ip"] = client_ip
        log_data["is_routable"] = is_routable

        logger.info(f"[HeaderDebug] {log_data}")

        return self.get_response(request)
