from os import path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import logging
from builtins import any

from django.http import FileResponse, Http404, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.defaults import permission_denied
from django.core.exceptions import DisallowedHost

from nsc.permissions import ReviewManagerRequiredMixin
from nsc.policy.models import Policy
from nsc.utils.datetime import get_today
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.http import is_same_domain
from urllib.parse import urlsplit


from ..document.models import Document
from .forms import (
    ReviewDateConfirmationForm,
    ReviewDatesForm,
    ReviewForm,
    ReviewHistoryForm,
    ReviewPublishForm,
    ReviewRecommendationForm,
    ReviewStakeholdersForm,
    ReviewSummaryForm,
)
from .models import Review

def csrf_failure(request, reason=""):
    logger = logging.getLogger(__name__)
    request_origin = request.META["HTTP_ORIGIN"]
    logger.warning(request_origin, "request origin")
    try:
        good_host = request.get_host()
    except DisallowedHost:
        logger.warning("DisallowedHost")
        pass
    else:
        good_origin = "%s://%s" % (
            "https" if request.is_secure() else "http",
            good_host,
        )
        logger.warning(good_origin, "good origin")
        if request_origin == good_origin:
            logger.warning("request origin is same as good origin")
            return True
    if request_origin in CsrfViewMiddleware.allowed_origins_exact:
        logger.warning("request origin in self.allows origins exacy")
        return True
    try:
        parsed_origin = urlsplit(request_origin)
        logger.warning(parsed_origin, "parsed origin")
    except ValueError:
        return False
    parsed_origin_scheme = parsed_origin.scheme
    parsed_origin_netloc = parsed_origin.netloc
    is_matched = any(
        is_same_domain(parsed_origin_netloc, host)
        for host in CsrfViewMiddleware.allowed_origin_subdomains.get(parsed_origin_scheme, ())
        )
    logger.warning(is_matched, "is matched")
    # Reuse Django's default 403 behaviour
    return permission_denied(request, reason=reason)


class ReviewDashboardView(ReviewManagerRequiredMixin, generic.TemplateView):
    template_name = "review/review_dashboard.html"

    def get_context_data(self, **kwargs):
        reviews = (
            Review.objects.in_progress()
            .select_related("user")
            .filter(user=self.request.user)
        )
        return super().get_context_data(reviews=reviews)


class ReviewList(ReviewManagerRequiredMixin, generic.TemplateView):
    template_name = "review/review_list.html"

    def get_context_data(self, **kwargs):
        reviews = Review.objects.in_progress().select_related("user")
        return super().get_context_data(reviews=reviews)


class ReviewDetail(ReviewManagerRequiredMixin, generic.DetailView):
    model = Review
    lookup_field = "slug"
    context_object_name = "review"


class ReviewAdd(ReviewManagerRequiredMixin, generic.CreateView):
    model = Review
    form_class = ReviewForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not kwargs["instance"]:
            kwargs["instance"] = self.model(user=self.request.user)
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        slug = self.request.GET.get("policy", None)
        if slug:
            policy = Policy.objects.filter(slug=slug).first()
            if policy:
                initial["policies"] = [policy.pk]
                initial["name"] = _("%s %d review" % (policy.name, get_today().year))
        return initial


class ReviewDelete(ReviewManagerRequiredMixin, generic.DeleteView):
    model = Review
    success_url = reverse_lazy("dashboard")


class ReviewDates(ReviewManagerRequiredMixin, generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewDatesForm
    template_name = "review/review_dates.html"

    def get_initial(self):
        initial = super().get_initial()

        start = self.object.consultation_start
        end = self.object.consultation_end
        meeting = self.object.nsc_meeting_date

        if start is None:
            initial["consultation_open"] = None
        else:
            initial["consultation_open"] = start == get_today()
            initial["consultation_start_day"] = start.day
            initial["consultation_start_month"] = start.month
            initial["consultation_start_year"] = start.year

        if end:
            initial["consultation_end_day"] = end.day
            initial["consultation_end_month"] = end.month
            initial["consultation_end_year"] = end.year

        if meeting:
            initial["nsc_meeting_date_day"] = meeting.day
            initial["nsc_meeting_date_month"] = meeting.month
            initial["nsc_meeting_date_year"] = meeting.year

        return initial

    def get_success_url(self):
        return reverse_lazy("review:open", kwargs={"slug": self.object.slug})


class ReviewStakeholders(ReviewManagerRequiredMixin, generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewStakeholdersForm
    template_name = "review/review_stakeholders.html"


class ReviewSummary(ReviewManagerRequiredMixin, generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewSummaryForm
    template_name = "review/review_summary.html"


class ReviewHistory(ReviewManagerRequiredMixin, generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewHistoryForm
    template_name = "review/review_history.html"


class ReviewRecommendation(ReviewManagerRequiredMixin, generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewRecommendationForm
    template_name = "review/review_recommendation.html"

    def get_success_url(self):
        return reverse("review:publish", kwargs={"slug": self.object.slug})


class ReviewPublish(ReviewManagerRequiredMixin, generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewPublishForm
    template_name = "review/review_publish.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            decision=(
                _("Recommended") if self.object.recommendation else _("Not Recommended")
            ),
        )


class ReviewDateConfirmation(ReviewManagerRequiredMixin, generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewDateConfirmationForm
    template_name = "review/review_date_confirmation.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            scheduled=self.object.consultation_start > get_today(), **kwargs
        )


class ReviewDocumentDownload(generic.DetailView):
    model = Review
    lookup_field = "slug"

    def get(self, *args, doc_type=None, **kwargs):
        documents = Document.objects.for_review(self.get_object()).filter(
            document_type=doc_type
        )

        if len(documents) == 0:
            raise Http404()
        elif len(documents) == 1:
            return FileResponse(documents[0].upload, as_attachment=True)
        else:
            with TemporaryDirectory() as d:
                zipfile_path = path.join(d, f"{doc_type}.zip")

                with ZipFile(zipfile_path, mode="w") as z:
                    for doc in documents:
                        z.writestr(doc.name, doc.upload.read())

                return FileResponse(open(zipfile_path, "rb"), as_attachment=True)
