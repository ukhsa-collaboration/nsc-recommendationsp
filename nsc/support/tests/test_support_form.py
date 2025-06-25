from django.conf import settings
from django.urls import reverse

import pytest

from nsc.notify.models import Email


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def valid_data():
    return {
        "name": "Mr Foo",
        "organisation": "",
        "role": "",
        "country": "England",
        "subject": "subject",
        "message": "message",
        "email": "foo@example.com",
    }


@pytest.fixture
def form(django_app):
    return django_app.get(reverse("support:contact")).forms[1]


def submit_form(form, data):
    form["name"] = data["name"]
    form["organisation"] = data["organisation"]
    form["role"] = data["role"]
    form["country"] = data["country"]
    form["subject"] = data["subject"]
    form["message"] = data["message"]
    form["email"] = data["email"]
    return form.submit()


@pytest.mark.parametrize(
    "name",
    (
        "",
        "  ",
        None,
    ),
)
def test_name_is_invalid_error_is_raised(form, name, valid_data):
    res = submit_form(form, {**valid_data, "name": name})

    assert not Email.objects.exists()
    assert res.request.path == reverse("support:contact")


@pytest.mark.parametrize("country", ("",))
def test_country_is_invalid_error_is_raised(form, country, valid_data):
    res = submit_form(form, {**valid_data, "country": country})

    assert not Email.objects.exists()
    assert res.request.path == reverse("support:contact")


@pytest.mark.parametrize(
    "subject",
    (
        "",
        "  ",
        None,
    ),
)
def test_subject_is_invalid_error_is_raised(form, subject, valid_data):
    res = submit_form(form, {**valid_data, "subject": subject})

    assert not Email.objects.exists()
    assert res.request.path == reverse("support:contact")


@pytest.mark.parametrize(
    "message",
    (
        "",
        "  ",
        None,
    ),
)
def test_message_is_invalid_error_is_raised(form, message, valid_data):
    res = submit_form(form, {**valid_data, "message": message})

    assert not Email.objects.exists()
    assert res.request.path == reverse("support:contact")


@pytest.mark.parametrize("email", ("", "  ", None, "not an email"))
def test_email_is_invalid_error_is_raised(form, email, valid_data):
    res = submit_form(form, {**valid_data, "email": email})

    assert not Email.objects.exists()
    assert res.request.path == reverse("support:contact")


def test_data_is_valid_email_is_created(form, valid_data):
    res = submit_form(form, valid_data)

    assert Email.objects.count() == 2
    assert Email.objects.filter(
        address=valid_data["email"],
        template_id=settings.NOTIFY_TEMPLATE_HELP_DESK_CONFIRMATION,
        context=valid_data,
    )
    assert Email.objects.filter(
        address=settings.PHE_HELP_DESK_EMAIL,
        template_id=settings.NOTIFY_TEMPLATE_HELP_DESK,
        context=valid_data,
    )
    assert res.location == reverse("support:complete") + "#"


@pytest.mark.usefixtures("settings")
def test_notify_429_renders_limit_exceeded_template(django_app, valid_data, settings):
    """
    Test that when the Notify 429 simulation is enabled, submitting the contact form
    returns the limit exceeded template and does not send any emails.
    """
    # Enable simulation in settings
    settings.SIMULATE_NOTIFY_429 = True

    # Page should render the limit template and not create emails
    form = django_app.get(reverse("support:contact")).forms[1]
    res = submit_form(form, valid_data)
    assert res.status_code == 429
    assert "You've reached the daily form submission limit" in res.text
    assert not Email.objects.exists()
