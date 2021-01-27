from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import pytest
from bs4 import BeautifulSoup

from nsc.contact.models import Contact
from nsc.stakeholder.models import Stakeholder


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.policy.tests.fixtures"]


@pytest.fixture
def policy(make_policy):
    return make_policy()


@pytest.fixture
def response(django_app):
    return django_app.get(reverse("stakeholder:add"))


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_add_view(response):
    """
    Test that the add stakeholder page can be displayed.
    """
    assert response.status == "200 OK"


def test_back_link(dom):
    """
    Test the back link returns to the stakeholder list page
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == reverse("stakeholder:list")
    assert link.text.strip() == _("Back to stakeholders")


def test_success_url(policy, response):
    """
    Test saving a contact returns to the stakeholder list page.
    """
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["type"] = Stakeholder.TYPE_INDIVIDUAL
    form["country"] = Stakeholder.COUNTRY_ENGLAND
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form["policies-0-policy"] = policy.id
    actual = form.submit().follow()
    assert actual.request.path == Stakeholder.objects.first().get_detail_url()


def test_stakeholder_created(policy, response):
    """
    Test that the stakeholder object is created.
    """
    assert Stakeholder.objects.count() == 0
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["type"] = Stakeholder.TYPE_INDIVIDUAL
    form["country"] = Stakeholder.COUNTRY_ENGLAND
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form["policies-0-policy"] = policy.id
    form.submit()
    assert Stakeholder.objects.count() == 1


def test_contact_created(policy, response):
    """
    Test that the stakeholder object is created.
    """
    assert Contact.objects.count() == 0
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["type"] = Stakeholder.TYPE_INDIVIDUAL
    form["country"] = Stakeholder.COUNTRY_ENGLAND
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form["policies-0-policy"] = policy.id
    form.submit()
    assert Contact.objects.count() == 1


def test_policy_is_linked(policy, response):
    """
    Test that the stakeholder object is created.
    """
    assert Contact.objects.count() == 0
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["type"] = Stakeholder.TYPE_INDIVIDUAL
    form["country"] = Stakeholder.COUNTRY_ENGLAND
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form["policies-0-policy"] = policy.id
    form.submit()
    assert Stakeholder.objects.count() == 1
    assert list(Stakeholder.objects.first().policies.values_list("id", flat=True)) == [
        policy.id
    ]
