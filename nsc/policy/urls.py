from django.urls import path

from . import views


urlpatterns = [
    path(r"", views.PolicyList.as_view(), name="list"),
    path(r"<slug:slug>/", views.PolicyDetail.as_view(), name="detail"),
    path(r"<slug:slug>/edit/", views.PolicyEdit.as_view(), name="edit"),
]

app_name = "policy"
