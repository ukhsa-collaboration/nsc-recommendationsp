import logging

from django.shortcuts import render

from notifications_python_client.errors import HTTPError


logger = logging.getLogger(__name__)


def render_notify_429(request):
    """
    Render a custom template when the GOV.UK Notify daily or rate limit is exceeded.
    """
    return render(
        request,
        "notify_limit_exceeded.html",
        {
            "ratelimit_message": (
                "You've reached the daily form submission limit.\n You can try again tomorrow, or go back to the previous page to download the form and submit it via email."
            )
        },
        status=429,
    )


class Notify429ExceptionMixin:
    """
    Mixin for Django class-based views to catch 429 errors from GOV.UK Notify.
    Renders a custom template when the daily or rate limit is hit.
    Use as the first base class in your CBV inheritance order.
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except HTTPError as e:
            status_code = getattr(e, "status_code", None)
            resp_status = getattr(getattr(e, "response", None), "status_code", None)
            if status_code == 429 or resp_status == 429:
                logger.warning("GOV.UK Notify 429 error caught in CBV: %s", e)
                return render_notify_429(request)
            raise
