from django_filters import CharFilter, FilterSet


class SearchFilter(FilterSet):
    condition = CharFilter(field_name="policies__name", method="filter_conditions")

    def filter_conditions(self, queryset, name, value):
        return queryset.filter(policies__name__icontains=value).distinct()
