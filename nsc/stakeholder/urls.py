from django.urls import path

from .views import (
    StakeholderAdd,
    StakeholderDelete,
    StakeholderDetail,
    StakeholderEdit,
    StakeholderExport,
    StakeholderList,
)


urlpatterns = [
    path(r"", StakeholderList.as_view(), name="list"),
    path(r"export/", StakeholderExport.as_view(), name="export"),
    path(r"add/", StakeholderAdd.as_view(), name="add"),
    path(r"<int:pk>/", StakeholderDetail.as_view(), name="detail"),
    path(r"<int:pk>/delete/", StakeholderDelete.as_view(), name="delete"),
    path(r"<int:pk>/edit/", StakeholderEdit.as_view(), name="edit"),
]

app_name = "stakeholder"
