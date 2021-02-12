from django.forms import inlineformset_factory

from nsc.stakeholder.models import Stakeholder

from .forms import ContactForm
from .models import Contact


# ContactFormSet is only used when adding a new Stakeholder so can_delete
# is disabled as it is not needed. If the user adds too many blank forms they
# will be ignored when the form is submitted.

ContactFormSet = inlineformset_factory(
    Stakeholder,
    Contact,
    fields=("name", "role", "email", "phone", "stakeholder"),
    form=ContactForm,
    extra=1,
    can_delete=False,
    min_num=0,
    max_num=5,
    validate_min=True,
)
