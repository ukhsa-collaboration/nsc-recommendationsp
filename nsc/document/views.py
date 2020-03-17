import mimetypes

from django.http import FileResponse, Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from nsc.review.models import Review

from .forms import ExternalReviewForm, ReviewDocumentsForm
from .models import Document


class AddExternalReviewView(generic.CreateView):
    template_name = "document/add_external_review.html"
    form_class = ExternalReviewForm

    def get_initial(self):
        initial = super().get_initial()
        review = Review.objects.get(slug=self.kwargs["slug"])
        initial.update(
            {
                "name": _("External review"),
                "document_type": Document.TYPE.external_review,
                "review": review.pk,
            }
        )
        return initial

    def get_context_data(self, **kwargs):
        review = Review.objects.get(slug=self.kwargs["slug"])
        return super().get_context_data(review=review, **kwargs)

    def get_object(self, queryset=None):
        # Get any existing external review document.
        pk = self.request.POST["review"]
        review = Review.objects.get(pk=pk)
        return review.get_external_review()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            existing = self.object.upload
        else:
            existing = None
        form = self.get_form()
        if form.is_valid():
            if existing:
                self.object.upload.storage.delete(existing.name)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("review:detail", kwargs={"slug": self.kwargs["slug"]})


class AddReviewDocumentsView(generic.FormView):
    template_name = "document/add_review_documents.html"
    form_class = ReviewDocumentsForm

    def get_context_data(self, **kwargs):
        review = Review.objects.get(slug=self.kwargs["slug"])
        return super().get_context_data(review=review, **kwargs)

    def get_success_url(self):
        return reverse("review:detail", kwargs={"slug": self.kwargs["slug"]})


class DownloadView(generic.DetailView):
    model = Document

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        storage = document.upload.storage

        if not storage.exists(document.upload.name):
            raise Http404

        mime_type, encoding = mimetypes.guess_type(document.upload.url)

        return FileResponse(
            storage.open(document.upload.path, "rb"),
            as_attachment=True,
            content_type=mime_type,
        )
