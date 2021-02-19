from django import forms
from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from django_filters import BooleanFilter, CharFilter, ChoiceFilter, Filter, FilterSet

from .forms import SearchForm
from .models import Policy


class AgeGroupFilter(SimpleListFilter):
    """Filter for the list of possible ages on a Condition.

    TODO
        * Current the choices method is overridden to allow conditions that
          specifically affect all ages to be distinguished from any condition.
          It might be better to replace this with a checklist filter so the
          use can specify more than one condition or revisit the model and
          decide on how 'None' and 'all ages' relate to each other i.e. does
          None mean 'not set' or 'all ages'.

    """

    title = _("Age Groups")
    parameter_name = "ages"

    def lookups(self, request, model_admin):
        return Policy.AGE_GROUPS

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": _("Any age group"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        lookup_value = self.value()
        if lookup_value:
            queryset = queryset.filter(ages__contains=[lookup_value])
        return queryset


# TODO All the following code is shared with condition/filters.py check
#     later once the development is finished to see if it can be shared.


class YesNoFilter(Filter):
    def filter(self, qs, value):
        if value is None:
            return qs
        lc_value = value.lower()
        if lc_value == "yes":
            value = True
        elif lc_value == "no":
            value = False
        return qs.filter(**{self.field_name: value})


class SearchFilter(FilterSet):

    name = CharFilter(field_name="name", method="search_name")
    review_status = CharFilter(method="in_consultation")
    recommendation = YesNoFilter(field_name="recommendation")
    archived = BooleanFilter(method="include_archived", widget=forms.CheckboxInput)
    comments = CharFilter(method="in_consultation")
    affects = ChoiceFilter(
        field_name="ages",
        lookup_expr="icontains",
        choices=Policy.AGE_GROUPS,
        empty_label=None,
        widget=forms.RadioSelect,
    )

    def search_name(self, queryset, name, value):
        return queryset.search(value)

    def in_consultation(self, queryset, name, value):
        if value == SearchForm.CONSULTATION.due:
            return queryset.overdue()
        elif value == SearchForm.CONSULTATION.in_review:
            return queryset.in_progress()
        elif value == SearchForm.CONSULTATION.in_consultation:
            return queryset.open_for_comments()
        elif value == SearchForm.CONSULTATION.post_consultation:
            return queryset.closed_for_comments()
        else:
            return queryset

    def include_archived(self, queryset, name, value):
        if value:
            return queryset
        else:
            return queryset.exclude_archived()
