from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from django_filters.views import FilterView

from nsc.policy.models import Policy
from nsc.utils.datetime import get_today

from .filters import SearchFilter
from .forms import (
    ReviewDatesForm,
    ReviewForm,
    ReviewOrganisationsForm,
    ReviewRecommendationForm,
    ReviewSummaryForm,
    SearchForm,
)
from .models import Review


class ReviewStatusView(generic.TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        reviews = Review.objects.draft()
        policies = (Policy.objects.upcoming() | Policy.objects.overdue()).order_by(
            "next_review"
        )
        return super().get_context_data(reviews=reviews, policies=policies)


class ReviewList(FilterView):
    queryset = Policy.objects.active()
    paginate_by = 20
    template_name = "review/review_list.html"
    filterset_class = SearchFilter

    def get_context_data(self, **kwargs):
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


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


class ReviewCancel(generic.DeleteView):
    model = Review

    def get_success_url(self):
        msg = _("%s was cancelled successfully" % self.object.name)
        messages.info(self.request, msg)
        return reverse("home")


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


class ReviewOrganisations(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewOrganisationsForm
    template_name = "review/review_organisations.html"


class ReviewSummary(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewSummaryForm
    template_name = "review/review_summary.html"


class ReviewRecommendation(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewRecommendationForm
    template_name = "review/review_recommendation.html"
