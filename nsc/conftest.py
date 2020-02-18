import random

import pytest
from model_bakery import baker


# A custom ArrayField was used to model the ages field on the Policy model
# so a better default widget would be available. While model bakery supports
# ArrayField it can't customized versions so we have to add a generator
# function that can be used to generate fake data. Ideally we should use the
# choices used on the model but that runs the risk of circular dependencies
# unless the choices are factored out but that makes things more obscure /
# complicated than necessary so we just use a random selection from a list
# of hard-wired values.

all_ages = ["{antenatal}", "{newborn}", "{child}", "{adult}", "{all}"]


def generate_ages():
    return random.choice(all_ages)


baker.generators.add("nsc.policy.fields.ChoiceArrayField", "nsc.conftest.generate_ages")


@pytest.fixture
def django_app_form(db, django_app):
    """
    Wrapper for django_app fixture - GET a form, fill it out and POST it back

    Usage:

        def test(django_app_form):
            response = django_app_form(url, field=value)
    """

    def get_and_post(url, **form_args):
        form = django_app.get(url).form
        for field, value in form_args.items():
            form[field] = value
        return form.submit()

    return get_and_post


@pytest.fixture
def set_session_variable(django_app):
    """
    Set a variable in the client session.

    Django-webtest does not support sessions out of the box. This fixes that.
    See, https://github.com/django-webtest/django-webtest/issues/68

    """

    def _set_var(key, value):
        django_app.set_cookie("sessionid", "initial")
        session = django_app.session
        session[key] = value
        session.save()
        django_app.set_cookie("sessionid", session.session_key)

    return _set_var
