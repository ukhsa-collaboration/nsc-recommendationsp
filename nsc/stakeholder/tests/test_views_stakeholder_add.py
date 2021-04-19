from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import pytest
from bs4 import BeautifulSoup

from nsc.contact.models import Contact
from nsc.stakeholder.models import Stakeholder


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def policy(make_policy):
    return make_policy()


@pytest.fixture
def url():
    return reverse("stakeholder:add")


@pytest.fixture
def response(url, erm_user, django_app):
    return django_app.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_add_view(response):
    """
    Test that the add stakeholder page can be displayed.
    """
    assert response.status == "200 OK"


def test_add_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_add_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_back_link(dom):
    """
    Test the back link returns to the stakeholder list page
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == reverse("stakeholder:list")
    assert link.text.strip() == _("Back")


def test_back_link__next(erm_user, django_app):
    """
    Test the back link returns to the stakeholder list page
    """
    response = django_app.get(reverse("stakeholder:add") + "?next=/", user=erm_user)
    dom = BeautifulSoup(response.content, "html.parser")
    link = dom.find(id="back-link-id")
    assert link["href"] == "/"
    assert link.text.strip() == _("Back")


def test_success_url(policy, response):
    """
    Test saving a contact returns to the stakeholder list page.
    """
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["type"] = Stakeholder.TYPE_INDIVIDUAL
    form["countries"] = [Stakeholder.COUNTRY_ENGLAND]
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form["policies-0-policy"] = policy.id
    actual = form.submit().follow()
    assert actual.request.path == Stakeholder.objects.first().get_detail_url()


def test_success_url__next(erm_user, policy, django_app):
    """
    Test saving a contact returns to the stakeholder list page.
    """
    response = django_app.get(f'{reverse("stakeholder:add")}?next=/', user=erm_user)
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["type"] = Stakeholder.TYPE_INDIVIDUAL
    form["countries"] = [Stakeholder.COUNTRY_ENGLAND]
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form["policies-0-policy"] = policy.id
    actual = form.submit().follow()
    assert actual.request.path == "/"


def test_stakeholder_created(policy, response):
    """
    Test that the stakeholder object is created.
    """
    assert Stakeholder.objects.count() == 0
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["type"] = Stakeholder.TYPE_INDIVIDUAL
    form["countries"] = [Stakeholder.COUNTRY_ENGLAND]
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
    form["countries"] = [Stakeholder.COUNTRY_ENGLAND]
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
    form["countries"] = [Stakeholder.COUNTRY_ENGLAND]
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form["policies-0-policy"] = policy.id
    form.submit()
    assert Stakeholder.objects.count() == 1
    assert list(Stakeholder.objects.first().policies.values_list("id", flat=True)) == [
        policy.id
    ]
