from django.urls import path

from .views import DownloadView


urlpatterns = [path(r"<int:pk>/download", DownloadView.as_view(), name="download")]

app_name = "document"
