from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.cache import add_never_cache_headers


class ReviewManagerRequiredMixin(PermissionRequiredMixin):
    permission_required = "review.evidence_review_manager"

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        add_never_cache_headers(response)
        return response
