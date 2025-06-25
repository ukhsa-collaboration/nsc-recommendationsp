from itertools import chain

from django.conf import settings
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic

from django_ratelimit.decorators import ratelimit

from nsc.mixins.ratelimitmixin import RatelimitExceptionMixin

from ..notify.models import Email
from .forms import (
    CreateStakeholderSubscriptionForm,
    CreateSubscriptionForm,
    ManageSubscriptionsForm,
    SubscriptionStart,
)
from .models import StakeholderSubscription, Subscription
from .signer import check_object, get_object_signature


class GetObjectFromTokenMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if not check_object(obj, self.kwargs["token"]):
            raise Http404()

        return obj


class SubscriptionLanding(generic.TemplateView):
    template_name = "subscription/subscription_landing.html"


class PublicSubscriptionStart(RatelimitExceptionMixin, generic.FormView):
    form_class = SubscriptionStart
    template_name = "subscription/public_subscription_management_form.html"

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "data": self.request.POST or self.request.GET or None,
        }

    def form_valid(self, form):
        if "save" in form.data:
            url = reverse("subscription:public-subscribe")

            selected_policies = chain(
                form.cleaned_data["hidden_policies"],
                form.cleaned_data["policies"],
            )
            selected_policies_qs = "&".join(
                map(
                    lambda p: f"policies={p.id}",
                    selected_policies,
                )
            )

            return HttpResponseRedirect(f"{url}?{selected_policies_qs}")
        else:
            return self.render_to_response(self.get_context_data(form=form))


<<<<<<< HEAD
class PublicSubscriptionManage(
    RatelimitExceptionMixin, GetObjectFromTokenMixin, generic.UpdateView
):
=======
@method_decorator(
    ratelimit(
        key="ip",
        rate=f"{settings.FORM_SUBMIT_LIMIT_PER_HOUR}/h",
        method="POST",
        block=True,
    ),
    name="post",
)
class PublicSubscriptionManage(GetObjectFromTokenMixin, generic.UpdateView):
>>>>>>> test/email-function
    model = Subscription
    form_class = ManageSubscriptionsForm
    template_name = "subscription/public_subscription_management_form.html"

    def get_success_url(self):
        return reverse(
            "subscription:public-complete",
            kwargs={"pk": self.object.pk, "token": get_object_signature(self.object)},
        )

    def handle_delete(self):
        with transaction.atomic():
            Email.objects.create(
                address=self.object.email,
                template_id=settings.NOTIFY_TEMPLATE_UNSUBSCRIBE,
                context={
                    "subscribe url": self.request.build_absolute_uri(
                        reverse("subscription:public-start")
                    ),
                },
            )
            self.object.delete()
        return HttpResponseRedirect(reverse("subscription:public-deleted"))

    def form_valid(self, form):
        if "save" in form.data:
            with transaction.atomic():
                Email.objects.create(
                    address=self.object.email,
                    template_id=settings.NOTIFY_TEMPLATE_UPDATED_SUBSCRIPTION,
                    context={
                        "manage subscription url": self.request.build_absolute_uri(
                            reverse(
                                "subscription:public-manage",
                                kwargs={
                                    "pk": form.instance.id,
                                    "token": get_object_signature(form.instance),
                                },
                            )
                        )
                    },
                )
                return super().form_valid(form)
        elif "delete" in form.data and self.object.id:
            return self.handle_delete()
        else:
            return self.render_to_response(self.get_context_data(form=form))


<<<<<<< HEAD
class PublicSubscriptionEmails(RatelimitExceptionMixin, generic.UpdateView):
=======
@method_decorator(
    ratelimit(
        key="ip",
        rate=f"{settings.FORM_SUBMIT_LIMIT_PER_HOUR}/h",
        method="POST",
        block=True,
    ),
    name="post",
)
class PublicSubscriptionEmails(generic.UpdateView):
>>>>>>> test/email-function
    model = Subscription
    form_class = CreateSubscriptionForm
    template_name = "subscription/public_subscription_email_form.html"

    def get_initial(self):
        return {"policies": self.request.GET.getlist("policies", [])}

    def get_object(self, queryset=None):
        data = self.request.POST or {}

        return Subscription.objects.filter(email=data.get("email", None)).first()

    def get_success_url(self):
        return reverse(
            "subscription:public-complete",
            kwargs={"pk": self.object.pk, "token": get_object_signature(self.object)},
        )

    def form_valid(self, form):
        res = super().form_valid(form)

        Email.objects.create(
            address=self.object.email,
            template_id=settings.NOTIFY_TEMPLATE_SUBSCRIBED,
            context={
                "policy list": "\n".join(
                    f"* {p}"
                    for p in self.object.policies.values_list(
                        "name", flat=True
                    ).order_by("name")
                ),
                "manage subscription url": self.request.build_absolute_uri(
                    reverse(
                        "subscription:public-manage",
                        kwargs={
                            "pk": form.instance.id,
                            "token": get_object_signature(form.instance),
                        },
                    )
                ),
            },
        )

        return res


class PublicSubscriptionComplete(GetObjectFromTokenMixin, generic.DetailView):
    model = Subscription
    template_name = "subscription/public_subscription_complete.html"


@method_decorator(
    ratelimit(
        key="ip",
        rate=f"{settings.FORM_SUBMIT_LIMIT_PER_HOUR}/h",
        method="POST",
        block=True,
    ),
    name="post",
)
class StakeholderSubscriptionStart(generic.CreateView):
    model = StakeholderSubscription
    template_name = "subscription/stakeholder_subscription_creation.html"
    form_class = CreateStakeholderSubscriptionForm
    success_url = reverse_lazy("subscription:stakeholder-complete")


class StakeholderSubscriptionComplete(generic.TemplateView):
    template_name = "subscription/stakeholder_subscription_complete.html"
