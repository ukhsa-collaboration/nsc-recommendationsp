from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from nsc.contact.formsets import ContactFormSet

from .filters import SearchFilter
from .forms import OrganisationForm, SearchForm
from .models import Organisation


class OrganisationList(generic.ListView):
    queryset = Organisation.objects.all().order_by("name")
    paginate_by = 20

    def get_queryset(self):
        return SearchFilter(self.request.GET, queryset=self.queryset).qs

    def get_context_data(self, **kwargs):
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class OrganisationDetail(generic.DetailView):
    model = Organisation

    def get_context_data(self, **kwargs):
        self.request.session["organisation"] = self.object.pk
        return super().get_context_data(**kwargs)


class OrganisationAdd(generic.CreateView):
    model = Organisation
    form_class = OrganisationForm
    template_name = "organisation/organisation_add.html"
    success_url = reverse_lazy("organisation:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["formsets"] = [ContactFormSet(self.request.POST or None)]
        return kwargs


class OrganisationEdit(generic.UpdateView):
    model = Organisation
    form_class = OrganisationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["field"] = self.kwargs["field"]
        return kwargs

    def get_success_url(self):
        return reverse("organisation:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["back_title"] = _("Back to %s" % self.object.name)
        context["back_url"] = self.get_success_url()
        return context


class OrganisationDelete(generic.DeleteView):
    model = Organisation

    def get_success_url(self):
        msg = _("%s was deleted successfully" % self.object.name)
        messages.info(self.request, msg)
        return reverse("organisation:list")
