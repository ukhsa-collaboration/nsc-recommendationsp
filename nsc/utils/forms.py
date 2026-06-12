from django import forms
from django.contrib.postgres.fields import ArrayField
from django.forms import SelectMultiple


def strtobool(val):
    val = str(val).lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value {val!r}")


class ArraySelectMultiple(SelectMultiple):
    def value_omitted_from_data(self, data, files, name):
        return False


class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.

    """

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
            "widget": ArraySelectMultiple,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)
