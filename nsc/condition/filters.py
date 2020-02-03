from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from .models import Condition


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
        return Condition.AGE_GROUPS

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
