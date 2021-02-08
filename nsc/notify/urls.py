from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from nsc.notify.views import ProcessSendReceipt


urlpatterns = [
    path("receipt/", csrf_exempt(ProcessSendReceipt.as_view()), name="receipt"),
]

app_name = "notify"
