from django.conf import settings
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.utils.translation import ugettext_lazy as _
from notifications_python_client.errors import HTTPError

from nsc.policy.models import Policy
from nsc.review.models import Review

from .filters import SearchFilter
from .forms import SearchForm, SubmissionForm
from ..utils.notify import send_submission_form


class ConditionList(ListView):
    template_name = "policy/public/policy_list.html"
    queryset = Policy.objects.active()
    paginate_by = 20

    def get_queryset(self):
        return SearchFilter(self.request.GET, queryset=self.queryset).qs

    def get_context_data(self, **kwargs):
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class ConditionDetail(DetailView):
    template_name = "policy/public/policy_detail.html"
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        referer = self.request.META.get("HTTP_REFERER", reverse("condition:list"))
        latest = Review.objects.for_policy(self.object).published().first()
        current = Review.objects.for_policy(self.object).in_consultation().first()
        context.update(
            {"back_url": referer, "latest_review": latest, "current_review": current}
        )
        return context


class ConsultationView(TemplateView):
    template_name = "policy/public/consultation.html"

    def get_context_data(self, **kwargs):
        condition = Policy.objects.get(slug=self.kwargs["slug"])
        review = Review.objects.for_policy(condition).in_consultation().first()
        email = settings.CONSULTATION_COMMENT_ADDRESS
        return super().get_context_data(
            condition=condition, review=review, email=email, **kwargs
        )


class SubmissionView(FormView):
    template_name = "policy/public/submission.html"
    form_class = SubmissionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        condition = Policy.objects.get(slug=self.kwargs["slug"])
        context["condition"] = condition
        context["form"].initial["condition"] = condition.name
        return context

    def get_success_url(self):
        return reverse("condition:submitted", kwargs={"slug": self.kwargs["slug"]})

    def form_valid(self, form):
        try:
            send_submission_form(form.cleaned_data)
        except HTTPError:
            form.add_error(
                None,
                _("There was a problem submitting your comment. Please try again."),
            )
            return super().form_invalid(form)

        return super().form_valid(form)


class SubmittedView(TemplateView):
    template_name = "policy/public/submitted.html"

    def get_context_data(self, **kwargs):
        condition = Policy.objects.get(slug=self.kwargs["slug"])
        review = Review.objects.for_policy(condition).in_consultation().first()
        return super().get_context_data(condition=condition, review=review, **kwargs)
