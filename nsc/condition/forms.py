from django import forms
from django.utils.translation import ugettext_lazy as _

from nsc.policy.models import Policy


class SearchForm(forms.Form):

    name = forms.CharField(label=_("Search by condition name"), required=False)

    affects = forms.TypedChoiceField(
        label=_("Who the condition affects"),
        choices=Policy.AGE_GROUPS,
        widget=forms.RadioSelect,
        required=False,
    )

    screen = forms.TypedChoiceField(
        label=_("Current recommendation"),
        choices=(("yes", _("Yes")), ("no", _("No"))),
        widget=forms.RadioSelect,
        required=False,
    )

    name.widget.attrs.update({"class": "govuk-input", "style": "width: 80%"})
    affects.widget.attrs.update({"class": "govuk-radios__input"})
    screen.widget.attrs.update({"class": "govuk-radios__input"})
