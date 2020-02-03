from django.urls import path

from . import views


urlpatterns = [
    path(r"", views.PolicyList.as_view(), name="list"),
    path(r"<slug:slug>/", views.PolicyDetail.as_view(), name="detail"),
]

app_name = "policy"
