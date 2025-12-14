from urllib.parse import urlparse

from django.http import HttpResponseRedirect

import logging
from django.middleware.csrf import CsrfViewMiddleware, is_same_domain
from django.conf import settings
from urllib.parse import urlsplit

logger = logging.getLogger('django.middleware.csrf')

class VerboseCsrfViewMiddleware(CsrfViewMiddleware):
    def _origin_verified(self, request):
        logger.debug(f"origin verified called")
        origin = request.META.get("HTTP_ORIGIN")
        try:
            good_host = request.get_host()
        except DisallowedHost:
            good_host = "<DisallowedHost>"
        good_scheme = "https" if request.is_secure() else "http"
        good_origin = f"{good_scheme}://{good_host}"
        
        keys = [
            "HTTP_HOST",
            "HTTP_X_FORWARDED_PROTO",
            "HTTP_X_FORWARDED_FOR",
            "HTTP_FORWARDED",
            "HTTP_X_FORWARDED_HOST",
            "SERVER_NAME",
            "SERVER_PORT",
            "REMOTE_ADDR",
            "wsgi.url_scheme",
            "REQUEST_SCHEME",
        ]

        for k in keys:
            logger.warning(f"{k}: {request.META.get(k)}")
        
        verified = super()._origin_verified(request)
        if verified:
            logger.debug(f"CSRF Origin VERIFIED: {origin} is a trusted origin.")
        else:
            # The super method handles specific reasons and logs them to 'django.security.csrf'
            # We can log the specific details for our custom logger
            trusted_origins = settings.CSRF_TRUSTED_ORIGINS
            allowed_hosts = settings.ALLOWED_HOSTS
            request_origin = request.META["HTTP_ORIGIN"]
            parsed_origin = urlsplit(request_origin)
            parsed_origin_scheme = parsed_origin.scheme
            parsed_origin_netloc = parsed_origin.netloc
            is_matched =  any(
            is_same_domain(parsed_origin_netloc, host)
            for host in self.allowed_origin_subdomains.get(parsed_origin_scheme, ())
        )
            logger.warning(
                f"CSRF Origin FAILED: Origin '{origin}' does not match any trusted origins or allowed hosts. "
                f"Trusted origins: {trusted_origins}. Allowed hosts: {allowed_hosts}."
                f"Parsed origins: {parsed_origin}. Is matched: {is_matched}."
                f"Parsed origins scheme: {parsed_origin_scheme}. Parsed origins netloc: {parsed_origin_netloc}."
            )
        return verified


def redirect_url_fragment(get_response):
    """
    Sets the fragment of the redirect urls
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



