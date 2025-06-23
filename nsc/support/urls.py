from django.urls import path
from django.views.generic import TemplateView

from .views import ContactHelpDesk


urlpatterns = [
    path("", ContactHelpDesk.as_view(), name="contact"),
    path(
        "complete/",
        TemplateView.as_view(template_name="support/complete.html"),
        name="complete",
    ),
]
app_name = "support"
