from django import forms

from django_filters import BooleanFilter, CharFilter, Filter, FilterSet

from nsc.condition.forms import SearchForm


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
    comments = CharFilter(method="in_consultation")
    affects = CharFilter(field_name="ages", lookup_expr="icontains")
    screen = YesNoFilter(field_name="recommendation")
    archived = BooleanFilter(method="include_archived", widget=forms.CheckboxInput)

    def search_name(self, queryset, name, value):
        return queryset.search(value)

    def in_consultation(self, queryset, name, value):
        if value == SearchForm.CONSULTATION.open:
            return queryset.open_for_comments()
        elif value == SearchForm.CONSULTATION.closed:
            return queryset.closed_for_comments()
        else:
            return queryset

    def include_archived(self, queryset, name, value):
        if value:
            return queryset
        else:
            return queryset.exclude_archived()
