import ipaddress
import logging

from django.conf import settings
from django.http import HttpResponseForbidden


logger = logging.getLogger(__name__)


class AdminIPRestrictionMiddleware:
    """
    Middleware to restrict access to Django admin endpoints based on allowed IP ranges.

    The allowed IP ranges are read from the DJANGO_ADMIN_IP_RANGES environment variable,
    which should be a comma-separated list of CIDR ranges (e.g. "1.2.3.4/32, 5.6.7.0/24").
    """

    def __init__(self, get_response):
        logger.info("AdminIPRestrictionMiddleware is initialized")
        self.get_response = get_response
        raw_ip_ranges = settings.DJANGO_ADMIN_IP_RANGES.strip()

        if not raw_ip_ranges:
            logger.warning(
                "DJANGO_ADMIN_IP_RANGES environment variable is required but not set."
                "If you want django-admin to be accessible to anyone on the internet (restrict no one), then set it to 0.0.0.0/0"
            )
            self.allowed_ips = []

        else:
            raw_ip_list = raw_ip_ranges.split(",")
            stripped_ips = [raw_ip.strip() for raw_ip in raw_ip_list if raw_ip.strip()]
            # Converting the strings into IPv4Network objects
            self.allowed_ips = [
                ipaddress.ip_network(stripped_ip) for stripped_ip in stripped_ips
            ]

    def __call__(self, request):
        admin_prefixes = ["/django-admin/", "/admin/"]
        if any(request.path.startswith(prefix) for prefix in admin_prefixes):
            ip = self.get_incoming_ip(request)
            logger.info(f"User attempted to access {request.path} from IP: {ip}")
            if not self.is_allowed_ip(ip):
                logger.warning(
                    f"403 Forbidden: IP {ip} not allowed to access django-admin."
                )
                return HttpResponseForbidden("403 Forbidden: IP not allowed.")
            logger.info(f"Access to django-admin granted for IP: {ip}")
        return self.get_response(request)

    def is_allowed_ip(self, ip):
        try:
            incoming_ip = ipaddress.ip_address(ip)
            return any(
                incoming_ip in allowed_range for allowed_range in self.allowed_ips
            )
        except ValueError:
            logger.error(f"Invalid IP address format: {ip}")
            return False

    def get_incoming_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        logger.info(f"X-Forwarded-For header: {x_forwarded_for}")
        logger.info(
            f"Given that requests come from Kemp Loadmaster, the following REMOTE_ADDR should be the loadmaster's internal ip: {request.META.get('REMOTE_ADDR', '')}"
        )
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        fallback_ip = request.META.get("REMOTE_ADDR", "")
        logger.info(f"X-Forwarded-For not found. Using REMOTE_ADDR: {fallback_ip}")
        return fallback_ip
