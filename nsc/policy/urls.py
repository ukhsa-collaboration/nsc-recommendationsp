from django.urls import include, path

from . import views


urlpatterns = [
    path(r"", views.PolicyList.as_view(), name="list"),
    path(r"<slug:slug>/", views.PolicyDetail.as_view(), name="detail"),
    path(r"<slug:slug>/edit/", views.PolicyEdit.as_view(), name="edit"),
]

archive_urlpatterns = (
    [
        path(r"<slug:slug>/", views.ArchiveDetail.as_view(), name="detail"),
        path(
            r"<slug:slug>/upload/",
            views.ArchiveDocumentUploadView.as_view(),
            name="upload",
        ),
        path(r"<slug:slug>/update/", views.ArchiveUpdate.as_view(), name="update"),
        path(
            r"<slug:slug>/complete/", views.ArchiveComplete.as_view(), name="complete"
        ),
    ],
    "archive",
)

urlpatterns += [
    path("archive/", include(archive_urlpatterns)),
]


app_name = "policy"
