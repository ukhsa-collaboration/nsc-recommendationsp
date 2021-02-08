from django.forms import modelform_factory
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views import generic

from .models import Email, ReceiptUserToken


class ProcessSendReceipt(generic.View):
    def post(self, request, *args, **kwargs):
        auth_header = str(request.META.get("HTTP_AUTHORIZATION", ""))
        split = auth_header.split(" ")

        # if we have a badly formed token or the token does not exist return forbidden
        if (
            len(split) != 2
            or split[0] != "bearer"
            or not ReceiptUserToken.objects.filter(token=split[1]).exists()
        ):
            return HttpResponseForbidden()

        # validate the new status
        form_cls = modelform_factory(Email, fields=["status"])
        form = form_cls(
            instance=get_object_or_404(Email, id=self.request.POST.get("reference")),
            data=request.POST,
        )
        if not form.is_valid():
            return HttpResponseBadRequest()

        # save the status change
        form.save()

        return HttpResponse()
