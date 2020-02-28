from django_filters import CharFilter, Filter, FilterSet


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
    affects = CharFilter(field_name="ages", lookup_expr="icontains")
    screen = YesNoFilter(field_name="is_screened")

    def search_name(self, queryset, name, value):
        return queryset.search(value)
