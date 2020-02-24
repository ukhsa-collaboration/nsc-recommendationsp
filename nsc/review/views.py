from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from django_filters.views import FilterView

from nsc.policy.models import Policy

from .filters import SearchFilter
from .forms import (
    SearchForm,
    ReviewForm,
    ReviewOrganisationsForm,
    ReviewAddOrganisationForm,
    ReviewDatesForm,
    ReviewConsultationForm,
    ReviewRecommendationForm,
)
from .models import Review


class ReviewStatusView(generic.TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        reviews = Review.objects.current()
        policies = Policy.objects.review_due()
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
    lookup_field = "slug"
    form_class = ReviewForm


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


class ReviewOrganisations(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewOrganisationsForm
    template_name = "review/review_organisations.html"


class ReviewAddOrganisation(generic.UpdateView):
    model = Review  # TODO change to organisation
    lookup_field = "slug"
    form_class = ReviewAddOrganisationForm
    template_name = "review/review_add_organisation.html"


class ReviewConsultation(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewConsultationForm
    template_name = "review/review_consultation.html"


class ReviewRecommendation(generic.UpdateView):
    model = Review
    lookup_field = "slug"
    form_class = ReviewRecommendationForm
    template_name = "review/review_recommendation.html"
