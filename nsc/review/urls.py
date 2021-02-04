from django.urls import path

from nsc.document.views import (
    AddExternalReviewView,
    AddReviewDocumentsView,
    AddSubmissionFormView,
)

from . import views


urlpatterns = [
    path(r"", views.ReviewList.as_view(), name="list"),
    path(r"add/", views.ReviewAdd.as_view(), name="add"),
    path(r"<slug:slug>/", views.ReviewDetail.as_view(), name="detail"),
    path(r"<slug:slug>/delete/", views.ReviewDelete.as_view(), name="delete"),
    path(r"<slug:slug>/dates/", views.ReviewDates.as_view(), name="dates"),
    path(
        r"<slug:slug>/dates/confirmation/",
        views.ReviewDateConfirmation.as_view(),
        name="open",
    ),
    path(
        r"<slug:slug>/stakeholders/",
        views.ReviewStakeholders.as_view(),
        name="stakeholders",
    ),
    path(
        r"<slug:slug>/recommendation/",
        views.ReviewRecommendation.as_view(),
        name="recommendation",
    ),
    path(r"<slug:slug>/summary/", views.ReviewSummary.as_view(), name="summary"),
    path(r"<slug:slug>/history/", views.ReviewHistory.as_view(), name="history"),
    path(
        r"<slug:slug>/add-external-review/",
        AddExternalReviewView.as_view(),
        name="add-external-review",
    ),
    path(
        r"<slug:slug>/add-submission-form/",
        AddSubmissionFormView.as_view(),
        name="add-submission-form",
    ),
    path(
        r"<slug:slug>/add-review-documents/",
        AddReviewDocumentsView.as_view(),
        name="add-review-documents",
    ),
]

app_name = "review"
