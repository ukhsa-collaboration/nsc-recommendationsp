from django.urls import path

from nsc.document.views import ContinueView, PolicyDocumentView, ReviewDocumentView

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
        r"<slug:slug>/organisation/add/",
        views.ReviewAddOrganisation.as_view(),
        name="organisation",
    ),
    path(
        r"<slug:slug>/consultation/",
        views.ReviewConsultation.as_view(),
        name="consultation",
    ),
    path(
        r"<slug:slug>/recommendation/",
        views.ReviewRecommendation.as_view(),
        name="recommendation",
    ),
    path(
        r"<slug:slug>/add-policy-document/",
        PolicyDocumentView.as_view(),
        name="add-policy-document",
    ),
    path(
        r"<slug:slug>/next-policy-document/",
        ContinueView.as_view(),
        name="next-policy-document",
    ),
    path(
        r"<slug:slug>/add-review-document/",
        ReviewDocumentView.as_view(),
        name="add-review-document",
    ),
]

app_name = "review"
