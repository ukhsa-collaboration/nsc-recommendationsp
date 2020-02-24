from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .forms import DocumentForm, UploadAnotherForm, ReviewDocumentForm
from .models import Document
from ..review.models import Review


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
        initial["document_type"] = Document.TYPES.policy
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


class ReviewDocumentView(DocumentView):
    template_name = "document/review_document_form.html"
    form_class = ReviewDocumentForm

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "name": _("Review document"),
                "is_public": False,
                "document_type": Document.TYPES.review,
            }
        )
        return initial

    def get_success_url(self):
        return reverse("review:detail", kwargs={"slug": self.kwargs["slug"]})


class RecommendationDocumentView(DocumentView):
    template_name = "document/recommendation_document_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["document_type"] = Document.TYPES.recommendation
        return initial
