from django.urls import path

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
