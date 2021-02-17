from django_filters import CharFilter, ChoiceFilter, FilterSet

from nsc.stakeholder.models import Stakeholder


class SearchFilter(FilterSet):

    name = CharFilter(field_name="name", lookup_expr="icontains")
    condition = CharFilter(field_name="policies__name", method="filter_conditions")
    country = ChoiceFilter(
        field_name="countries",
        choices=Stakeholder.COUNTRY_CHOICES,
        lookup_expr="icontains",
    )

    def filter_conditions(self, queryset, name, value):
        return queryset.filter(policies__name__icontains=value).distinct()
