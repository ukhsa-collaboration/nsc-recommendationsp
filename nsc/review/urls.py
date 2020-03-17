from django.urls import path

from nsc.document.views import AddExternalReviewView, AddReviewDocumentsView

from . import views


urlpatterns = [
    path(r"", views.ReviewList.as_view(), name="list"),
    path(r"add/", views.ReviewAdd.as_view(), name="add"),
    path(r"<slug:slug>/", views.ReviewDetail.as_view(), name="detail"),
    path(r"<slug:slug>/cancel/", views.ReviewCancel.as_view(), name="cancel"),
    path(r"<slug:slug>/dates/", views.ReviewDates.as_view(), name="dates"),
    path(
        r"<slug:slug>/organisations/",
        views.ReviewOrganisations.as_view(),
        name="organisations",
    ),
    path(
        r"<slug:slug>/recommendation/",
        views.ReviewRecommendation.as_view(),
        name="recommendation",
    ),
    path(r"<slug:slug>/summary/", views.ReviewSummary.as_view(), name="add-summary"),
    path(
        r"<slug:slug>/add-external-review/",
        AddExternalReviewView.as_view(),
        name="add-external-review",
    ),
    path(
        r"<slug:slug>/add-review-documents/",
        AddReviewDocumentsView.as_view(),
        name="add-review-documents",
    ),
]

app_name = "review"
