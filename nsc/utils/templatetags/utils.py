from django import template


register = template.Library()


@register.filter
def get(obj, prop):
    return getattr(obj, prop, None)
