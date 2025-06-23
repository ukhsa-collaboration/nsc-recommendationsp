from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator

from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited


def render_custom_403(request, exception=None):
    if isinstance(exception, Ratelimited) or getattr(request, "limited", False):
        ratelimit_message = "Too many requests. Please try again later."
        return render(
            request,
            "form_limit_exceeded.html",
            {"ratelimit_message": ratelimit_message},
            status=403,
        )
    else:
        raise PermissionDenied


class RatelimitExceptionMixin:
    @method_decorator(
        ratelimit(
            key="ip",
            rate=f"{settings.FORM_SUBMIT_LIMIT_PER_MINUTE}/m",
            method="POST",
            block=False,
        )
    )
    def dispatch(self, request, *args, **kwargs):
        # Check if rate limit was exceeded
        if getattr(request, "limited", False):
            # You can optionally pass a Ratelimited instance for compatibility
            return render_custom_403(request, exception=Ratelimited())
        return super().dispatch(request, *args, **kwargs)
