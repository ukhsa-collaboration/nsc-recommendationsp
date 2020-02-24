from django.urls import path

from .views import (
    ConditionDetail,
    ConditionList,
    ConsultationView,
    SubmissionView,
    SubmittedView,
)


urlpatterns = [
    path(r"", ConditionList.as_view(), name="list"),
    path(r"<slug:slug>/", ConditionDetail.as_view(), name="detail"),
    path(r"<slug:slug>/consultation/", ConsultationView.as_view(), name="consultation"),
    path(r"<slug:slug>/submission/", SubmissionView.as_view(), name="submission"),
    path(r"<slug:slug>/submitted/", SubmittedView.as_view(), name="submitted"),
]

app_name = "condition"
