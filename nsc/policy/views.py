from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from django_filters.views import FilterView

from nsc.permissions import AdminRequiredMixin

from .filters import SearchFilter
from .forms import (
    ArchiveForm,
    OptionalPolicyDocumentForm,
    PolicyAddForm,
    PolicyAddRecommendationForm,
    PolicyAddSummaryForm,
    PolicyDocumentForm,
    PolicyEditForm,
    SearchForm,
)
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


class PolicyList(AdminRequiredMixin, FilterView):
    model = Policy
    paginate_by = 20
    template_name = "policy/admin/policy_list.html"
    filterset_class = SearchFilter

    def get_queryset(self):
        return Policy.objects.active().prefetch_reviews_in_consultation()

    def get_context_data(self, **kwargs):
        # Setting the from on the filter does not quite work so we pass
        # it in explicitly, for now.
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class PolicyDetail(AdminRequiredMixin, DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/policy_detail.html"

    def get_object(self, queryset=None):
        return super().get_object(
            queryset=self.get_queryset().prefetch_related("reviews")
        )


class PolicyAddMixin(AdminRequiredMixin):
    model = Policy
    section = None
    next_section = None
    markdown_guide = False

    def get_success_url(self):
        return reverse(f"policy:add:{self.next_section}", args=(self.object.slug,))

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            section=self.section, markdown_guide=self.markdown_guide, **kwargs
        )


class PolicyAdd(PolicyAddMixin, CreateView):
    form_class = PolicyAddForm
    model = Policy
    template_name = "policy/admin/add/start.html"
    section = "start"
    next_section = "summary"
    markdown_guide = True


class PolicyAddSummary(PolicyAddMixin, UpdateView):
    form_class = PolicyAddSummaryForm
    lookup_field = "slug"
    template_name = "policy/admin/add/summary.html"
    section = "summary"
    next_section = "recommendation"
    markdown_guide = True


class PolicyAddDocument(PolicyAddMixin, UpdateView):
    """
    Note - after a discussion with Adrian, this overlaps with review and for now will not be used
    until there is a document that needs to be capture and is therefore not used in the add flow.
    """

    form_class = OptionalPolicyDocumentForm
    lookup_field = "slug"
    template_name = "policy/admin/add/document.html"
    section = "document"
    next_section = "recommendation"


class PolicyAddRecommendation(SuccessMessageMixin, PolicyAddMixin, UpdateView):
    form_class = PolicyAddRecommendationForm
    lookup_field = "slug"
    template_name = "policy/admin/add/recommendation.html"
    section = "recommendation"
    success_message = "Condition recommendation has been created"

    def get_success_url(self):
        return reverse("review:add") + f"?policy={self.object.slug}"


class PolicyEdit(AdminRequiredMixin, PublishPreviewMixin, UpdateView):
    model = Policy
    lookup_field = "slug"
    form_class = PolicyEditForm
    template_name = "policy/admin/policy_edit_form.html"
    success_url = reverse_lazy("policy:list")
    success_message = "Published changes to conditions page."


class ArchiveDetail(AdminRequiredMixin, DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/detail.html"


class ArchiveDocumentDetail(AdminRequiredMixin, DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/document.html"


class ArchiveDocumentUploadView(AdminRequiredMixin, UpdateView):
    form_class = PolicyDocumentForm
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/upload.html"

    def get_success_url(self):
        return reverse("policy:archive:upload", kwargs={"slug": self.kwargs["slug"]})


class ArchiveUpdate(AdminRequiredMixin, PublishPreviewMixin, UpdateView):
    form_class = ArchiveForm
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/update.html"

    def get_success_url(self):
        return reverse("policy:archive:complete", kwargs={"slug": self.kwargs["slug"]})


class ArchiveComplete(AdminRequiredMixin, PublishPreviewMixin, DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/archive/complete.html"
