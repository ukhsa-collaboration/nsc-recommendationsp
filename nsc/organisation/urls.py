from django.urls import path

from .views import (
    OrganisationAdd,
    OrganisationDelete,
    OrganisationDetail,
    OrganisationEdit,
    OrganisationList,
)


urlpatterns = [
    path(r"", OrganisationList.as_view(), name="list"),
    path(r"add/", OrganisationAdd.as_view(), name="add"),
    path(r"<pk>/", OrganisationDetail.as_view(), name="detail"),
    path(r"<pk>/delete/", OrganisationDelete.as_view(), name="delete"),
    path(r"<pk>/edit/<field>/", OrganisationEdit.as_view(), name="edit"),
]

app_name = "organisation"
