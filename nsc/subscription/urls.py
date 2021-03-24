from django.urls import path
from django.views.generic import TemplateView

from .views import (
    PublicSubscriptionComplete,
    PublicSubscriptionEmails,
    PublicSubscriptionManage,
    PublicSubscriptionStart,
    StakeholderSubscriptionComplete,
    StakeholderSubscriptionStart,
    SubscriptionLanding,
)


urlpatterns = [
    path("", SubscriptionLanding.as_view(), name="landing"),
    path("public-start/", PublicSubscriptionStart.as_view(), name="public-start"),
    path(
        "public-subscribe/", PublicSubscriptionEmails.as_view(), name="public-subscribe"
    ),
    path(
        "public-manage/<int:pk>/<slug:token>/",
        PublicSubscriptionManage.as_view(),
        name="public-manage",
    ),
    path(
        "public-complete/<int:pk>/<slug:token>/",
        PublicSubscriptionComplete.as_view(),
        name="public-complete",
    ),
    path(
        "public-deleted/",
        TemplateView.as_view(
            template_name="subscription/public_subscription_deleted.html"
        ),
        name="public-deleted",
    ),
    path(
        "stakeholder-start/",
        StakeholderSubscriptionStart.as_view(),
        name="stakeholder-start",
    ),
    path(
        "stakeholder-complete/",
        StakeholderSubscriptionComplete.as_view(),
        name="stakeholder-complete",
    ),
]

app_name = "subscription"
