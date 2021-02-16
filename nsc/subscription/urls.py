from django.urls import path

from .views import (
    PublicSubscribe,
    PublicSubscribeStart,
    StakeholderSubscribeStart,
    StakeholderSubscriptionComplete,
    SubscribeLanding,
    SubscriptionComplete,
    publicManageSubscription,
)


urlpatterns = [
    path("", SubscribeLanding.as_view(), name="landing"),
    path("public-start/", PublicSubscribeStart.as_view(), name="public-start"),
    path("public-subscribe/", PublicSubscribe.as_view(), name="public-subscribe"),
    path(
        "public-manage/<int:pk>/<slug:token>/",
        publicManageSubscription.as_view(),
        name="public-manage",
    ),
    path(
        "public-complete/<int:pk>/<slug:token>/",
        SubscriptionComplete.as_view(),
        name="public-complete",
    ),
    path(
        "stakeholder-start/",
        StakeholderSubscribeStart.as_view(),
        name="stakeholder-start",
    ),
    path(
        "stakeholder-complete/",
        StakeholderSubscriptionComplete.as_view(),
        name="stakeholder-complete",
    ),
]

app_name = "subscription"
