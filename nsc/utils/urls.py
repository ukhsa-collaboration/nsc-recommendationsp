from django.shortcuts import render
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme

from django_ratelimit.exceptions import Ratelimited


def clean_url(target, default, allowed_hosts, require_secure):
    if target:
        i18n_target = iri_to_uri(target)
        is_safe = url_has_allowed_host_and_scheme(
            url=i18n_target, allowed_hosts=allowed_hosts, require_https=require_secure
        )
        if is_safe:
            return i18n_target

    return default


def render_custom_403(request, exception=None):
    print("Custom 403 handler called!")
    if isinstance(exception, Ratelimited):
        message = "Form submission limit excceded. Please try again later."
    else:
        message = "You do not have permission to access this page."
    return render(request, "403.html", {"message": message}, status=403)
