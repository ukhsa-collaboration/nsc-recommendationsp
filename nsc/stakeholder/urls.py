from django.urls import path

from .views import (
    StakeholderAdd,
    StakeholderDelete,
    StakeholderDetail,
    StakeholderEdit,
    StakeholderList,
)


urlpatterns = [
    path(r"", StakeholderList.as_view(), name="list"),
    path(r"add/", StakeholderAdd.as_view(), name="add"),
    path(r"<pk>/", StakeholderDetail.as_view(), name="detail"),
    path(r"<pk>/delete/", StakeholderDelete.as_view(), name="delete"),
    path(r"<pk>/edit/", StakeholderEdit.as_view(), name="edit"),
]

app_name = "stakeholder"
