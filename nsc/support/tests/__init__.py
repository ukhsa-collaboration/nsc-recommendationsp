from django.conf import settings
from django.urls import reverse

import pytest

from nsc.notify.models import Email


@pytest.fixture
def valid_data():
    return {
        "name": "Mr Foo",
        "organisation": "",
        "role": "",
        "region": "North",
        "subject": "subject",
        "message": "message",
        "email": "foo@example.com",
    }


@pytest.fixture
def form(django_app):
    return django_app.get(reverse("support:contact")).form


def submit_form(form, data):
    form["name"] = data["name"]
    form["organisation"] = data["organisation"]
    form["role"] = data["role"]
    form["region"] = data["region"]
    form["subject"] = data["subject"]
    form["message"] = data["message"]
    form["email"] = data["email"]
    return form.submit()


@pytest.mark.parametrize("name", ("", "  ", None,))
def test_name_is_invalid_error_is_raised(form, name, valid_data):
    res = submit_form(form, {**valid_data, "name": name})

    assert not Email.objects.exists()
    assert res.path == reverse("support:contact")


@pytest.mark.parametrize("region", ("", "  ", None,))
def test_region_is_invalid_error_is_raised(form, region, valid_data):
    res = submit_form(form, {**valid_data, "region": region})

    assert not Email.objects.exists()
    assert res.path == reverse("support:contact")


@pytest.mark.parametrize("subject", ("", "  ", None,))
def test_subject_is_invalid_error_is_raised(form, subject, valid_data):
    res = submit_form(form, {**valid_data, "subject": subject})

    assert not Email.objects.exists()
    assert res.path == reverse("support:contact")


@pytest.mark.parametrize("message", ("", "  ", None,))
def test_message_is_invalid_error_is_raised(form, message, valid_data):
    res = submit_form(form, {**valid_data, "message": message})

    assert not Email.objects.exists()
    assert res.path == reverse("support:contact")


@pytest.mark.parametrize("email", ("", "  ", None, "not an email"))
def test_email_is_invalid_error_is_raised(form, email, valid_data):
    res = submit_form(form, {**valid_data, "email": email})

    assert not Email.objects.exists()
    assert res.path == reverse("support:contact")


def test_data_is_valid_email_is_created(valid_data):
    res = submit_form(form, valid_data)

    assert Email.objects.cotunt() == 1
    assert Email.objects.filter(
        address=settings.PHE_HELP_DESK_EMAIL,
        template_id=settings.NOTIFY_TEMPLATE_HELP_DESK,
        context=valid_data,
    )
    assert res.location.path == reverse("support:complete")
