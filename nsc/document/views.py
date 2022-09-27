import mimetypes

from django.core.cache import cache
from django.http import FileResponse, Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from nsc.permissions import ReviewManagerRequiredMixin
from nsc.review.models import Review

from ..utils.urls import clean_url
from .forms import ExternalReviewForm, ReviewDocumentsForm, SubmissionForm
from .models import Document


class AddExternalReviewView(ReviewManagerRequiredMixin, generic.UpdateView):
    template_name = "document/add_external_review.html"
    form_class = ExternalReviewForm
    model = Review
    lookup_field = "slug"
    context_object_name = "review"

    def get_success_url(self):
        return clean_url(
            self.request.POST.get("next"),
            reverse("review:detail", kwargs={"slug": self.kwargs["slug"]}),
            [self.request.get_host()],
            self.request.is_secure(),
        )


class AddSubmissionFormView(ReviewManagerRequiredMixin, generic.CreateView):
    template_name = "document/add_submission_form.html"
    form_class = SubmissionForm

    def get_initial(self):
        initial = super().get_initial()
        review = Review.objects.get(slug=self.kwargs["slug"])
        initial.update(
            {
                "name": _("Response form"),
                "document_type": Document.TYPE.submission_form,
                "review": review.pk,
            }
        )
        return initial

    def get_context_data(self, **kwargs):
        review = Review.objects.get(slug=self.kwargs["slug"])
        return super().get_context_data(review=review, **kwargs)

    def get_object(self, queryset=None):
        # Get any existing response form.
        pk = self.request.POST["review"]
        review = Review.objects.get(pk=pk)
        return review.submission_form

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
        return clean_url(
            self.request.POST.get("next"),
            reverse("review:detail", kwargs={"slug": self.kwargs["slug"]}),
            [self.request.get_host()],
            self.request.is_secure(),
        )


class AddReviewDocumentsView(ReviewManagerRequiredMixin, generic.UpdateView):
    template_name = "document/add_review_documents.html"
    form_class = ReviewDocumentsForm
    model = Review
    slug_url_kwarg = "slug"
    context_object_name = "review"

    def get_success_url(self):
        return clean_url(
            self.request.POST.get("next"),
            reverse("review:detail", kwargs={"slug": self.kwargs["slug"]}),
            [self.request.get_host()],
            self.request.is_secure(),
        )


class DownloadView(generic.DetailView):
    model = Document

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        storage = document.upload.storage

        if not storage.exists(document.upload.name):
            raise Http404

        mime_type, encoding = mimetypes.guess_type(document.upload.url)

        return FileResponse(
            document.upload.open("rb"),
            as_attachment=True,
            content_type=mime_type,
        )


class DeleteView(ReviewManagerRequiredMixin, generic.DeleteView):
    model = Document

    def get_success_url(self):
        return clean_url(
            self.request.POST.get("next"),
            reverse("dashboard"),
            [self.request.get_host()],
            self.request.is_secure(),
        )

    def post(self, *args, **kwargs):
        res = super().post(*args, **kwargs)
        cache.clear()
        return res
