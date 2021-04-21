from django.urls import reverse

import pytest

from ..models import StakeholderSubscription


pytestmark = pytest.mark.django_db


def test_emails_dont_match_error_is_raised(django_app):
    url = reverse("subscription:stakeholder-start")

    response = django_app.get(url)

    form = response.form
    form["title"] = "mr"
    form["first_name"] = "Foo"
    form["last_name"] = "Bar"
    form["email"] = "foo@example.com"
    form["email_confirmation"] = "bar@example.com"
    form.submit()

    assert not StakeholderSubscription.objects.exists()


def test_fields_are_complete_subscription_is_created(django_app):
    url = reverse("subscription:stakeholder-start")

    response = django_app.get(url)

    form = response.form
    form["title"] = "mr"
    form["first_name"] = "Foo"
    form["last_name"] = "Bar"
    form["organisation"] = "Big Co."
    form["email"] = "foo@example.com"
    form["email_confirmation"] = "foo@example.com"
    response = form.submit()

    sub = StakeholderSubscription.objects.first()
    assert StakeholderSubscription.objects.count() == 1
    assert sub.email == "foo@example.com"
    assert sub.title == "mr"
    assert sub.first_name == "Foo"
    assert sub.last_name == "Bar"
    assert sub.organisation == "Big Co."
    assert response.location == reverse("subscription:stakeholder-complete") + "#"
