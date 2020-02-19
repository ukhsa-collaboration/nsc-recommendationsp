from django.urls import path

from .views import ContactAdd, ContactDelete, ContactEdit


urlpatterns = [
    path(r"add/<int:org_pk>/", ContactAdd.as_view(), name="add"),
    path(r"<int:pk>/delete/", ContactDelete.as_view(), name="delete"),
    path(r"<int:pk>/edit/", ContactEdit.as_view(), name="edit"),
]

app_name = "contact"
