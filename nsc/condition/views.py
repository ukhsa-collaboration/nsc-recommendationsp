from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, FormView, ListView, TemplateView

from django_ratelimit.decorators import ratelimit

from nsc.notify.models import Email
from nsc.policy.models import Policy
from nsc.review.models import Review
from nsc.subscription.models import Subscription

from ..utils.urls import clean_url
from .filters import SearchFilter
from .forms import PublicCommentForm, SearchForm, StakeholderCommentForm


class ConditionList(ListView):
    template_name = "policy/public/policy_list.html"
    model = Policy
    paginate_by = 20

    def get_queryset(self):
        return SearchFilter(
            self.request.GET,
            queryset=Policy.objects.active().prefetch_reviews_in_consultation(),
        ).qs

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

        default_back_url = reverse("condition:list")
        back_url = self.request.META.get("HTTP_REFERER", default_back_url)

        context.update(
            {
                "back_url": clean_url(
                    back_url,
                    default_back_url,
                    [self.request.get_host()],
                    self.request.is_secure(),
                ),
                "status_options": Review.STATUS,
            }
        )
        return context


class ConsultationMixin:
    @staticmethod
    def get_condition(slug):
        return get_object_or_404(
            Policy.objects.prefetch_related("reviews").open_for_comments(), slug=slug
        )


class ConsultationView(ConsultationMixin, TemplateView):
    template_name = "policy/public/consultation.html"

    def get_context_data(self, **kwargs):
        condition = self.get_condition(slug=self.kwargs["slug"])
        review = condition.reviews.open_for_comments().first()
        email = settings.CONSULTATION_COMMENT_ADDRESS
        return super().get_context_data(
            condition=condition, review=review, email=email, **kwargs
        )


@method_decorator(
    ratelimit(key="ip", rate=f"{settings.RATE_LIMIT}/h", method="POST", block=True),
    name="post",
)
class PublicCommentView(ConsultationMixin, FormView):
    template_name = "policy/public/public_comment.html"
    form_class = PublicCommentForm

    def get_success_url(self):
        return reverse(
            "condition:public-comment-submitted", kwargs={"slug": self.kwargs["slug"]}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        condition = self.get_condition(slug=self.kwargs["slug"])
        context["condition"] = condition
        context["form"].initial["condition"] = condition.name
        context["current_review"] = condition.current_review
        context["comment_fields"] = [
            context["form"][f] for f in self.form_class.COMMENT_FIELDS.keys()
        ]
        return context

    def form_valid(self, form):
        valid = super().form_valid(form)
        if valid:
            Email.objects.create(
                address=settings.CONSULTATION_COMMENT_ADDRESS,
                template_id=settings.NOTIFY_TEMPLATE_PUBLIC_COMMENT,
                context={
                    **form.cleaned_data,
                    "affected comment": form.cleaned_data["comment_affected"],
                    "evidence comment": form.cleaned_data["comment_evidence"],
                    "discussion comment": form.cleaned_data["comment_discussion"],
                    "recommendation comment": form.cleaned_data[
                        "comment_recommendation"
                    ],
                    "alternatives comment": form.cleaned_data["comment_alternatives"],
                    "other comment": form.cleaned_data["comment_other"],
                    "affected comment present": (
                        "yes" if form.cleaned_data["comment_affected"] else "no"
                    ),
                    "evidence comment present": (
                        "yes" if form.cleaned_data["comment_evidence"] else "no"
                    ),
                    "discussion comment present": (
                        "yes" if form.cleaned_data["comment_discussion"] else "no"
                    ),
                    "recommendation comment present": (
                        "yes" if form.cleaned_data["comment_recommendation"] else "no"
                    ),
                    "alternatives comment present": (
                        "yes" if form.cleaned_data["comment_alternatives"] else "no"
                    ),
                    "other comment present": (
                        "yes" if form.cleaned_data["comment_other"] else "no"
                    ),
                },
            )

            if form.cleaned_data.get("notify") == "True":
                subscription, _ = Subscription.objects.get_or_create(
                    email=form.cleaned_data.get("email")
                )
                subscription.policies.add(self.get_condition(slug=self.kwargs["slug"]))

        return valid


class PublicCommentSubmittedView(ConsultationMixin, TemplateView):
    template_name = "policy/public/public_comment_submitted.html"

    def get_context_data(self, **kwargs):
        condition = self.get_condition(slug=self.kwargs["slug"])
        review = condition.reviews.open_for_comments().first()
        url = settings.PROJECT_FEEDBACK_URL
        return super().get_context_data(
            condition=condition, review=review, feedback_url=url, **kwargs
        )


@method_decorator(
    ratelimit(key="ip", rate=f"{settings.RATE_LIMIT}/h", method="POST", block=True),
    name="post",
)
class StakeholderCommentView(ConsultationMixin, FormView):
    template_name = "policy/public/stakeholder_comment.html"
    form_class = StakeholderCommentForm

    def get_success_url(self):
        return reverse(
            "condition:stakeholder-comment-submitted",
            kwargs={"slug": self.kwargs["slug"]},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        condition = self.get_condition(slug=self.kwargs["slug"])
        context["condition"] = condition
        context["current_review"] = condition.current_review
        context["form"].initial["condition"] = condition.name

        return context

    def form_valid(self, form):
        valid = super().form_valid(form)
        if valid:
            Email.objects.create(
                address=settings.CONSULTATION_COMMENT_ADDRESS,
                template_id=settings.NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT,
                context=form.cleaned_data,
            )

        return valid


class StakeholderCommentSubmittedView(ConsultationMixin, TemplateView):
    template_name = "policy/public/stakeholder_comment_submitted.html"

    def get_context_data(self, **kwargs):
        condition = self.get_condition(slug=self.kwargs["slug"])
        review = condition.current_review
        url = settings.PROJECT_FEEDBACK_URL
        return super().get_context_data(
            condition=condition, review=review, feedback_url=url, **kwargs
        )
