from django.forms import inlineformset_factory

from nsc.organisation.models import Organisation

from .forms import ContactForm
from .models import Contact


# ContactFormSet is only used when adding a new Organisation so can_delete
# is disabled as it is not needed. If the user adds too many blank forms they
# will be ignored when the form is submitted.

ContactFormSet = inlineformset_factory(
    Organisation,
    Contact,
    fields=("name", "email", "phone", "organisation"),
    form=ContactForm,
    extra=0,
    can_delete=False,
    min_num=1,
    validate_min=True,
)
