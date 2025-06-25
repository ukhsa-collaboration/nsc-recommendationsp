from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator

from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited


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
            },
            status=429,
        )
    else:
        raise PermissionDenied


class RatelimitExceptionMixin:
    @method_decorator(
        ratelimit(
            key="ip",
            rate=f"{settings.FORM_SUBMIT_LIMIT_PER_HOUR}/d",
            method="POST",
            block=False,
        )
    )
    def dispatch(self, request, *args, **kwargs):
        # Check if rate limit was exceeded
        if getattr(request, "limited", False):
            # You can optionally pass a Ratelimited instance for compatibility
            return handle_429(request, exception=Ratelimited())
        return super().dispatch(request, *args, **kwargs)
