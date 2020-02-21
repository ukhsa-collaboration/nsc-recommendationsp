from django_filters import CharFilter, FilterSet


class SearchFilter(FilterSet):

    name = CharFilter(field_name="name", lookup_expr="icontains")
    condition = CharFilter(field_name="policies__name", method="filter_conditions")

    def filter_conditions(self, queryset, name, value):
        return queryset.filter(policies__name__icontains=value).distinct()
