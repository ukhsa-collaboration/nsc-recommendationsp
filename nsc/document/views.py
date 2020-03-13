import mimetypes

from django.http import FileResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from nsc.review.models import Review

from .forms import DocumentForm, EvidenceReviewUploadForm, UploadAnotherForm
from .models import Document


class DocumentView(generic.CreateView):
    model = Document
    form_class = DocumentForm

    def get_initial(self):
        initial = super().get_initial()
        review = Review.objects.get(slug=self.kwargs["slug"])
        initial["review"] = review.pk
        return initial

    def get_context_data(self, **kwargs):
        review = Review.objects.get(slug=self.kwargs["slug"])
        return super().get_context_data(review=review, **kwargs)


class PolicyDocumentView(DocumentView):
    template_name = "document/policy_document_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["document_type"] = Document.TYPE.recommendation
        return initial

    def get_success_url(self):
        return reverse(
            "review:next-policy-document", kwargs={"slug": self.kwargs["slug"]}
        )


class ContinueView(generic.FormView):
    template_name = "document/policy_document_continue.html"
    form_class = UploadAnotherForm

    def get_success_url(self):
        return reverse(
            "review:next-policy-document", kwargs={"slug": self.kwargs["slug"]}
        )

    def form_valid(self, form):
        slug = self.kwargs["slug"]
        if form.cleaned_data["another"]:
            url = reverse("review:add-policy-document", kwargs={"slug": slug})
        else:
            url = reverse("review:detail", kwargs={"slug": slug})
        return HttpResponseRedirect(url)


class EvidenceReviewUploadView(DocumentView):
    template_name = "document/evidence_review_upload.html"
    form_class = EvidenceReviewUploadForm

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "name": _("Evidence review"),
                "is_public": True,
                "document_type": Document.TYPE.evidence_review,
            }
        )
        return initial

    def get_object(self, queryset=None):
        # Since there is only ever on external evidence review if the
        # file was already uploaded, fetch the existing Document and
        # delete the file so everything can be overwritten.
        pk = self.request.POST["review"]
        review = Review.objects.get(pk=pk)
        document = review.get_evidence_review_document()
        if document:
            document.delete_file()
        return document

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("review:detail", kwargs={"slug": self.kwargs["slug"]})


class RecommendationDocumentView(DocumentView):
    template_name = "document/recommendation_document_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["document_type"] = Document.TYPE.recommendation
        return initial


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
