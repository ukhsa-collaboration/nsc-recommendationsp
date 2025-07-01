import logging
from django.core.cache import cache
from django.shortcuts import render


logger = logging.getLogger(__name__)

RATE_LIMIT_HIT_COUNT_TTL = 86400  # 24 hours
RATE_LIMIT_THRESHOLD = 5  # Set your desired threshold here


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # First IP is the original client
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def handle_rate_limit_exceeded(request, hit_count):
    logger.info(
        f"[RateLimit Exceeded] IP={get_client_ip(request)}, path={request.path}, hits={hit_count}"
    )
    return render(
        request,
        "form_limit_exceeded.html",
        {
            "ratelimit_headline": "You've reached the daily form submission limit.",
            "ratelimit_detail": "You can try again tomorrow, or email uknsc@dhsc.gov.uk if you have any queries.",
        },
        status=429,
    )


class RatelimitExceptionMixin:
    def dispatch(self, request, *args, **kwargs):
        client_ip = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "unknown")
        cache_key = f"hitcount:{client_ip}:{request.path}"

        try:
            hit_count = cache.incr(cache_key)
        except ValueError:
            cache.set(cache_key, 1, timeout=RATE_LIMIT_HIT_COUNT_TTL)
            hit_count = 1

        # Optional logging
        logger.info({
            "ip": client_ip,
            "user_agent": user_agent,
            "path": request.path,
            "hit_count": hit_count,
            "RATE_LIMIT_THRESHOLD": RATE_LIMIT_THRESHOLD
        })

        # Custom rate limit threshold check
        if hit_count > RATE_LIMIT_THRESHOLD:
            return handle_rate_limit_exceeded(request, hit_count)

        return super().dispatch(request, *args, **kwargs)
