from django.urls import path

from .views import (
    ConditionDetail,
    ConditionList,
    ConsultationView,
    PublicCommentSubmittedView,
    PublicCommentView,
    StakeholderCommentSubmittedView,
    StakeholderCommentView,
)


urlpatterns = [
    path(r"", ConditionList.as_view(), name="list"),
    path(r"<slug:slug>/", ConditionDetail.as_view(), name="detail"),
    path(r"<slug:slug>/consultation/", ConsultationView.as_view(), name="consultation"),
    path(
        r"<slug:slug>/public/comment/",
        PublicCommentView.as_view(),
        name="public-comment",
    ),
    path(
        r"<slug:slug>/public/comment/submitted/",
        PublicCommentSubmittedView.as_view(),
        name="public-comment-submitted",
    ),
    path(
        r"<slug:slug>/stakeholder/comment/",
        StakeholderCommentView.as_view(),
        name="stakeholder-comment",
    ),
    path(
        r"<slug:slug>/stakeholder/comment/submitted/",
        StakeholderCommentSubmittedView.as_view(),
        name="stakeholder-comment-submitted",
    ),
]

app_name = "condition"
