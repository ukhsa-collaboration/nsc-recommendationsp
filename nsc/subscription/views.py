from django.http import Http404
from django.urls import reverse
from django.views import generic

from .forms import CreateSubscriptionForm, ManageSubscriptionsForm, SubscriptionStart
from .models import Subscription
from .signer import check_object, get_object_signature


class GetObjectFromTokenMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if not check_object(obj, self.kwargs["token"]):
            raise Http404()

        return obj


class SubscribeStart(generic.FormView):
    form_class = SubscriptionStart
    template_name = "subscription/subscription_management_form.html"


class ManageSubscription(GetObjectFromTokenMixin, generic.UpdateView):
    model = Subscription
    form_class = ManageSubscriptionsForm
    template_name = "subscription/subscription_management_form.html"

    def get_success_url(self):
        return reverse(
            "subscription:complete",
            kwargs={"pk": self.object.pk, "token": get_object_signature(self.object)},
        )


class Subscribe(generic.UpdateView):
    model = Subscription
    form_class = CreateSubscriptionForm
    template_name = "subscription/subscription_creation_form.html"

    def get_initial(self):
        return {"policies": self.request.GET.getlist("policies", [])}

    def get_object(self, queryset=None):
        data = self.request.POST or {}

        return Subscription.objects.filter(email=data.get("email", None)).first()

    def get_success_url(self):
        return reverse(
            "subscription:complete",
            kwargs={"pk": self.object.pk, "token": get_object_signature(self.object)},
        )


class SubscriptionComplete(GetObjectFromTokenMixin, generic.DetailView):
    model = Subscription
    template_name = "subscription/subscription_complete.html"
