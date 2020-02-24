from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView, FormView

from nsc.policy.models import Policy

from .filters import SearchFilter
from .forms import SearchForm, SubmissionForm


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
        referer = self.request.META.get("HTTP_REFERER", reverse("condition:list"))
        return super().get_context_data(back_url=referer)


class ConsultationView(TemplateView):
    template_name = "policy/public/consultation.html"

    def get_context_data(self, **kwargs):
        condition = Policy.objects.get(slug=self.kwargs["slug"])
        return super().get_context_data(condition=condition, **kwargs)


class SubmissionView(FormView):
    template_name = "policy/public/submission.html"
    form_class = SubmissionForm

    def get_context_data(self, **kwargs):
        condition = Policy.objects.get(slug=self.kwargs["slug"])
        return super().get_context_data(condition=condition, **kwargs)

    def get_success_url(self):
        return reverse("condition:submitted", kwargs={"slug": self.kwargs["slug"]})


class SubmittedView(TemplateView):
    template_name = "policy/public/submitted.html"

    def get_context_data(self, **kwargs):
        condition = Policy.objects.get(slug=self.kwargs["slug"])
        return super().get_context_data(condition=condition, **kwargs)
