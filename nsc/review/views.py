from os import path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.http import FileResponse, Http404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from nsc.permissions import ReviewManagerRequiredMixin
from nsc.policy.models import Policy
from nsc.utils.datetime import get_today

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


class ReviewAdd(ReviewManagerRequiredMixin, generic.CreateView
):
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


class ReviewStakeholders(ReviewManagerRequiredMixin, generic.UpdateView
):
    model = Review
    lookup_field = "slug"
    form_class = ReviewStakeholdersForm
    template_name = "review/review_stakeholders.html"


class ReviewSummary(ReviewManagerRequiredMixin, generic.UpdateView
):
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


class ReviewPublish(ReviewManagerRequiredMixin, generic.UpdateView
):
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
