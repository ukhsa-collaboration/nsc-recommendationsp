from django.contrib.auth.mixins import PermissionRequiredMixin


class AdminRequiredMixin(PermissionRequiredMixin):
    permission_required = "review.evidence_review_manager"
