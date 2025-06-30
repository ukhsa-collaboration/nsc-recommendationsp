from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator

from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
import logging


logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # First IP is the original client
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def handle_429(request, exception=None):
    if isinstance(exception, Ratelimited) or getattr(request, "limited", False):
        ratelimit_headline = "You've reached the daily form submission limit."
        ratelimit_detail = "You can try again tomorrow, or Please email uknsc@dhsc.gov.uk if you have any queries."
        return render(
            request,
            "form_limit_exceeded.html",
            {
                "ratelimit_headline": ratelimit_headline,
                "ratelimit_detail": ratelimit_detail,
                "rate_limited": True
            },
            status=429,
        )
    else:
        raise PermissionDenied


class RatelimitExceptionMixin:
    @method_decorator(
        ratelimit(
            key="user_or_ip",
            rate=f"{settings.FORM_SUBMIT_LIMIT_PER_DAY}/d",
            method="POST",
            block=False,
        )
    )
    def dispatch(self, request, *args, **kwargs):
        client_ip = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "unknown")
        client_id = request.COOKIES.get("client_id", "no-client-id")
        log_info = {
            "ip": client_ip,
            "user_agent": user_agent,
            "client_id": client_id,
            "path": request.path,
            "limited": getattr(request, "limited", False)
        }
        logger.info(f"[RateLimit Check] {log_info}")

        # Check if rate limit was exceeded
        if getattr(request, "limited", False):
            logger.warning(f"[RateLimit Hit] IP={client_ip} exceeded rate limit on {request.path}")
            # You can optionally pass a Ratelimited instance for compatibility
            return handle_429(request, exception=Ratelimited())
        return super().dispatch(request, *args, **kwargs)
