from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from nsc.policy.models import Policy
from nsc.utils.datetime import get_today

from .forms import (
    ReviewDateConfirmationForm,
    ReviewDatesForm,
    ReviewForm,
    ReviewHistoryForm,
    ReviewRecommendationForm,
    ReviewStakeholdersForm,
    ReviewSummaryForm,
)
from .models import Review


class ReviewDashboardView(generic.TemplateView):
    template_name = "review/review_dashboard.html"

    def get_context_data(self, **kwargs):
        reviews = Review.objects.in_progress()
        return super().get_context_data(reviews=reviews)


class ReviewList(generic.TemplateView):
    template_name = "review/review_list.html"

    def get_context_data(self, **kwargs):
        reviews = Review.objects.in_progress()
        return super().get_context_data(reviews=reviews)


class ReviewDetail(generic.DetailView):
    model = Review
    lookup_field = "slug"
    context_object_name = "review"


class ReviewAdd(generic.CreateView):
    model = Review
    form_class = ReviewForm

    def get_initial(self):
        initial = super().get_initial()
        slug = self.request.GET.get("policy", None)
        if slug:
            policy = Policy.objects.filter(slug=slug).first()
            if policy:
                initial["policies"] = [policy.pk]
                initial["name"] = _("%s %d review" % (policy.name, get_today().year))
        return initial


class ReviewDelete(generic.DeleteView):
    model = Review
    success_url = reverse_lazy("dashboard")


class ReviewDates(generic.UpdateView):
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


class ReviewStakeholders(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewStakeholdersForm
    template_name = "review/review_stakeholders.html"


class ReviewSummary(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewSummaryForm
    template_name = "review/review_summary.html"


class ReviewHistory(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewHistoryForm
    template_name = "review/review_history.html"


class ReviewRecommendation(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewRecommendationForm
    template_name = "review/review_recommendation.html"


class ReviewDateConfirmation(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewDateConfirmationForm
    template_name = "review/review_date_confirmation.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            scheduled=self.object.consultation_start > get_today(), **kwargs
        )
