from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, TemplateView

from notifications_python_client.errors import HTTPError

from nsc.notify.client import submit_public_comment, submit_stakeholder_comment
from nsc.policy.models import Policy

from .filters import SearchFilter
from .forms import PublicCommentForm, SearchForm, StakeholderCommentForm


class ConditionList(ListView):
    template_name = "policy/public/policy_list.html"
    queryset = Policy.objects.active().prefetch_reviews_in_consultation()
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

    def get_object(self, queryset=None):
        return super().get_object(
            queryset=self.get_queryset().prefetch_related("reviews")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        referer = self.request.META.get("HTTP_REFERER", reverse("condition:list"))
        context.update({"back_url": referer})
        return context


class ConsultationView(TemplateView):
    template_name = "policy/public/consultation.html"

    def get_context_data(self, **kwargs):
        condition = Policy.objects.prefetch_related("reviews").get(
            slug=self.kwargs["slug"]
        )
        review = condition.reviews.open_for_comments().first()
        email = settings.CONSULTATION_COMMENT_ADDRESS
        return super().get_context_data(
            condition=condition, review=review, email=email, **kwargs
        )


class PublicCommentView(FormView):
    template_name = "policy/public/public_comment.html"
    form_class = PublicCommentForm

    def get_success_url(self):
        return reverse(
            "condition:public-comment-submitted", kwargs={"slug": self.kwargs["slug"]}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        condition = Policy.objects.get(slug=self.kwargs["slug"])
        context["condition"] = condition
        context["form"].initial["condition"] = condition.name
        return context

    def form_valid(self, form):
        try:
            submit_public_comment(form.cleaned_data)
        except HTTPError:
            form.add_error(
                None,
                _("There was a problem submitting your comment. Please try again."),
            )
            return super().form_invalid(form)

        return super().form_valid(form)


class PublicCommentSubmittedView(TemplateView):
    template_name = "policy/public/public_comment_submitted.html"

    def get_context_data(self, **kwargs):
        condition = Policy.objects.prefetch_related("reviews").get(
            slug=self.kwargs["slug"]
        )
        review = condition.reviews.open_for_comments().first()
        url = settings.PROJECT_FEEDBACK_URL
        return super().get_context_data(
            condition=condition, review=review, feedback_url=url, **kwargs
        )


class StakeholderCommentView(FormView):
    template_name = "policy/public/stakeholder_comment.html"
    form_class = StakeholderCommentForm

    def get_success_url(self):
        return reverse(
            "condition:stakeholder-comment-submitted",
            kwargs={"slug": self.kwargs["slug"]},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        condition = Policy.objects.get(slug=self.kwargs["slug"])
        context["condition"] = condition
        context["form"].initial["condition"] = condition.name
        return context

    def form_valid(self, form):
        try:
            submit_stakeholder_comment(form.cleaned_data)
        except HTTPError:
            form.add_error(
                None,
                _("There was a problem submitting your comment. Please try again."),
            )
            return super().form_invalid(form)

        return super().form_valid(form)


class StakeholderCommentSubmittedView(TemplateView):
    template_name = "policy/public/stakeholder_comment_submitted.html"

    def get_context_data(self, **kwargs):
        condition = Policy.objects.prefetch_related("reviews").get(
            slug=self.kwargs["slug"]
        )
        review = condition.reviews.open_for_comments().first()
        url = settings.PROJECT_FEEDBACK_URL
        return super().get_context_data(
            condition=condition, review=review, feedback_url=url, **kwargs
        )
