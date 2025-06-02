from django.urls import path

from .views import DeleteView, DownloadView


urlpatterns = [
    path(r"<uuid:uuid>/download", DownloadView.as_view(), name="download"),
    path(r"<uuid:uuid>/delete", DeleteView.as_view(), name="delete"),
]

app_name = "document"
