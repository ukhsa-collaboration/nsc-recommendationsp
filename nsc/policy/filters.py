from django_filters import FilterSet, CharFilter, Filter


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


class PolicyFilter(FilterSet):

    condition = CharFilter(field_name='name', lookup_expr='icontains')
    affects = CharFilter(field_name='condition__ages', lookup_expr='icontains')
    screen = YesNoFilter(field_name='is_screened')
