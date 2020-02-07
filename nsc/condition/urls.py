from django.urls import path

from .views import ConditionDetail, ConditionList


urlpatterns = [
    path(r"", ConditionList.as_view(), name="list"),
    path(r"<slug:slug>/", ConditionDetail.as_view(), name="detail"),
]

app_name = "condition"
