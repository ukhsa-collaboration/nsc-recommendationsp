from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme


def clean_url(target, default, allowed_hosts, require_secure):
    if target:
        i18n_target = iri_to_uri(target)
        is_safe = url_has_allowed_host_and_scheme(
            url=i18n_target, allowed_hosts=allowed_hosts, require_https=require_secure
        )
        if is_safe:
            return i18n_target

    return default
