import json
from urllib.parse import parse_qs, urlencode, urlsplit

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def get(obj, prop):
    return getattr(obj, prop, None)


@register.simple_tag(takes_context=True)
def update_qs(context, url=None, **params):
    url = url or context.request.build_absolute_uri()

    # split up the existing url
    split = urlsplit(url)

    # replace all the prams from the original url with the
    # new ones appending new params
    orig_params = parse_qs(split.query)
    updated_params = {**orig_params, **params}

    return f"{split.scheme}://{split.netloc}{split.path}?{urlencode(updated_params, doseq=True)}"


@register.filter
def as_json(value):
    return mark_safe(json.dumps(value))
