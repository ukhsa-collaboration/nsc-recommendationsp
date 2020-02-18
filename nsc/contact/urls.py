from django.urls import path

from .views import ContactAdd, ContactDelete, ContactEdit


urlpatterns = [
    path(r"add/", ContactAdd.as_view(), name="add"),
    path(r"<pk>/delete/", ContactDelete.as_view(), name="delete"),
    path(r"<pk>/edit/", ContactEdit.as_view(), name="edit"),
]

app_name = "contact"
