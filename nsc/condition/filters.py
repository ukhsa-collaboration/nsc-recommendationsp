from django.db.models import Q
from django_filters import CharFilter, Filter, FilterSet

from nsc.review.models import Review


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

    def search_name(self, queryset, name, value):
        return queryset.search(value)

    def in_consultation(self, queryset, name, value):
        if value == "open":
            return queryset.in_consultation()
        elif value == "closed":
            return queryset.not_in_consultation()
        else:
            return queryset
