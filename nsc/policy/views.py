from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, UpdateView

from django_filters.views import FilterView

from .filters import SearchFilter
from .forms import ArchiveDocumentForm, ArchiveForm, PolicyForm, SearchForm
from .models import Policy


class PublishPreviewMixin:
    success_message = None

    def is_preview(self):
        return self.request.POST.get("preview")

    def is_publish(self):
        return self.request.POST.get("publish")

    def form_valid(self, form):
        if self.is_publish():
            response = super().form_valid(form=form)
            success_message = self.success_message
            if success_message:
                messages.success(self.request, success_message)
            return response
        else:
            return self.render_to_response(
                self.get_context_data(form=form, preview=self.is_preview())
            )


class PolicyList(FilterView):
    queryset = Policy.objects.active().prefetch_reviews_in_consultation()
    paginate_by = 20
    template_name = "policy/admin/policy_list.html"
    filterset_class = SearchFilter

    def get_context_data(self, **kwargs):
        # Setting the from on the filter does not quite work so we pass
        # it in explicitly, for now.
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class PolicyDetail(DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/policy_detail.html"


class PolicyEdit(PublishPreviewMixin, UpdateView):
    model = Policy
    lookup_field = "slug"
    form_class = PolicyForm
    template_name = "policy/admin/policy_form.html"
    success_url = reverse_lazy("policy:list")
    success_message = "Published changes to conditions page."


class ArchiveDetail(DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/detail.html"


class ArchiveDocumentDetail(DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/document.html"


class ArchiveDocumentUploadView(UpdateView):
    form_class = ArchiveDocumentForm
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/upload.html"

    def get_success_url(self):
        return reverse("policy:archive:upload", kwargs={"slug": self.kwargs["slug"]})


class ArchiveUpdate(PublishPreviewMixin, UpdateView):
    form_class = ArchiveForm
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/update.html"
    success_message = "This recommendation has been archived"

    def get_success_url(self):
        return reverse("policy:detail", kwargs={"slug": self.kwargs["slug"]})
