from django.core.cache import cache


def clear_cache(*args, **kwargs):
    cache.clear()
