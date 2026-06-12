from django_filters import CharFilter, FilterSet, TypedChoiceFilter

from nsc.utils.forms import strtobool

from .forms import SearchForm


class SearchFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    # ToDo change the field name to the correct one
    status = TypedChoiceFilter(
        field_name="name", choices=SearchForm.REVIEW_STATUS_CHOICES
    )
    screen = TypedChoiceFilter(
        field_name="recommendation", choices=SearchForm.YES_NO_CHOICES, coerce=strtobool
    )
