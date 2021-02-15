from django.urls import path

from .views import ManageSubscription, Subscribe, SubscribeStart, SubscriptionComplete


urlpatterns = [
    path("start/", SubscribeStart.as_view(), name="start"),
    path("subscribe/", Subscribe.as_view(), name="subscribe"),
    path("manage/<int:pk>/<slug:token>/", ManageSubscription.as_view(), name="manage"),
    path(
        "complete/<int:pk>/<slug:token>/",
        SubscriptionComplete.as_view(),
        name="complete",
    ),
]

app_name = "subscription"
