from django.urls import path

from .views import DeleteView, DownloadView


urlpatterns = [
    path(r"<int:pk>/download", DownloadView.as_view(), name="download"),
    path(r"<int:pk>/delete", DeleteView.as_view(), name="delete"),
]

app_name = "document"
