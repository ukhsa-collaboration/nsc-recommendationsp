from django.utils.encoding import iri_to_uri
from django.utils.http import is_safe_url


def clean_url(target, default, allowed_hosts, require_secure):
    if target:
        i18n_target = iri_to_uri(target)
        is_safe = is_safe_url(
            url=i18n_target, allowed_hosts=allowed_hosts, require_https=require_secure
        )
        if is_safe:
            return i18n_target

    return default
