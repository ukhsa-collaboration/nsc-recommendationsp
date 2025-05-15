from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
def response(url, erm_user, client):
    client.force_login(erm_user)
    return client.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_add_view(response):
    """
    Test that the add stakeholder page can be displayed.
    """
    assert response.status_code == 200


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


def test_back_link__next(erm_user, client):
    """
    Test the back link returns to the stakeholder list page
    """
    client.force_login(erm_user)
    response = client.get(reverse("stakeholder:add") + "?next=/", user=erm_user)
    dom = BeautifulSoup(response.content, "html.parser")
    link = dom.find(id="back-link-id")
    assert link["href"] == "/"
    assert link.text.strip() == _("Back")


def test_success_url(policy, response, client):
    """
    Test saving a contact returns to the stakeholder list page.
    """
    post_data = {
        "name": "Name",
        "is_public": True,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": [Stakeholder.COUNTRY_ENGLAND],
        "contacts-0-name": "Name",
        "contacts-0-email": "name@example.com",
        "policies-0-policy": policy.id,
        # include form management data for formsets
        "contacts-TOTAL_FORMS": "1",
        "contacts-INITIAL_FORMS": "0",
        "contacts-MIN_NUM_FORMS": "0",
        "contacts-MAX_NUM_FORMS": "1000",
        "policies-TOTAL_FORMS": "1",
        "policies-INITIAL_FORMS": "0",
        "policies-MIN_NUM_FORMS": "0",
        "policies-MAX_NUM_FORMS": "1000",
    }

    response = client.post(reverse("stakeholder:add"), data=post_data, follow=True)

    expected_path = reverse("stakeholder:detail", args=[Stakeholder.objects.first().pk])
    assert response.request["PATH_INFO"] == expected_path


def test_success_url__next(erm_user, policy, client):
    """
    Test saving a contact returns to the stakeholder list page.
    """
    client.force_login(erm_user)

    url = f'{reverse("stakeholder:add")}?next=/'

    post_data = {
        "name": "Name",
        "is_public": True,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": [Stakeholder.COUNTRY_ENGLAND],
        # Contact formset
        "contacts-TOTAL_FORMS": "1",
        "contacts-INITIAL_FORMS": "0",
        "contacts-MIN_NUM_FORMS": "0",
        "contacts-MAX_NUM_FORMS": "1000",
        "contacts-0-name": "Name",
        "contacts-0-email": "name@example.com",
        # Policy formset
        "policies-TOTAL_FORMS": "1",
        "policies-INITIAL_FORMS": "0",
        "policies-MIN_NUM_FORMS": "0",
        "policies-MAX_NUM_FORMS": "1000",
        "policies-0-policy": policy.id,
    }

    response = client.post(url, data=post_data, follow=True)

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == "/"


def test_stakeholder_created(policy, client, erm_user):
    """
    Test that the stakeholder object is created.
    """
    client.force_login(erm_user)
    assert Stakeholder.objects.count() == 0

    post_data = {
        "name": "Name",
        "is_public": True,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": [Stakeholder.COUNTRY_ENGLAND],
        # Contact formset
        "contacts-TOTAL_FORMS": "1",
        "contacts-INITIAL_FORMS": "0",
        "contacts-MIN_NUM_FORMS": "0",
        "contacts-MAX_NUM_FORMS": "1000",
        "contacts-0-name": "Name",
        "contacts-0-email": "name@example.com",
        # Policy formset
        "policies-TOTAL_FORMS": "1",
        "policies-INITIAL_FORMS": "0",
        "policies-MIN_NUM_FORMS": "0",
        "policies-MAX_NUM_FORMS": "1000",
        "policies-0-policy": policy.id,
    }

    client.post(reverse("stakeholder:add"), data=post_data)

    assert Stakeholder.objects.count() == 1


def test_contact_created(policy, client, erm_user):
    """
    Test that the stakeholder object is created.
    """
    client.force_login(erm_user)

    assert Contact.objects.count() == 0

    post_data = {
        "name": "Name",
        "is_public": True,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": [Stakeholder.COUNTRY_ENGLAND],
        # Contact formset
        "contacts-TOTAL_FORMS": "1",
        "contacts-INITIAL_FORMS": "0",
        "contacts-MIN_NUM_FORMS": "0",
        "contacts-MAX_NUM_FORMS": "1000",
        "contacts-0-name": "Name",
        "contacts-0-email": "name@example.com",
        # Policy formset
        "policies-TOTAL_FORMS": "1",
        "policies-INITIAL_FORMS": "0",
        "policies-MIN_NUM_FORMS": "0",
        "policies-MAX_NUM_FORMS": "1000",
        "policies-0-policy": policy.id,
    }

    client.post(reverse("stakeholder:add"), data=post_data)

    # assert response.status_code in (302, 200)
    assert Contact.objects.count() == 1


def test_policy_is_linked(policy, client, erm_user):
    """
    Test that the stakeholder object is created.
    """
    client.force_login(erm_user)

    assert Contact.objects.count() == 0
    assert Stakeholder.objects.count() == 0

    post_data = {
        "name": "Name",
        "is_public": True,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": [Stakeholder.COUNTRY_ENGLAND],
        # Contact formset
        "contacts-TOTAL_FORMS": "1",
        "contacts-INITIAL_FORMS": "0",
        "contacts-MIN_NUM_FORMS": "0",
        "contacts-MAX_NUM_FORMS": "1000",
        "contacts-0-name": "Name",
        "contacts-0-email": "name@example.com",
        # Policy formset
        "policies-TOTAL_FORMS": "1",
        "policies-INITIAL_FORMS": "0",
        "policies-MIN_NUM_FORMS": "0",
        "policies-MAX_NUM_FORMS": "1000",
        "policies-0-policy": policy.id,
    }

    client.post(reverse("stakeholder:add"), data=post_data)

    assert Stakeholder.objects.count() == 1

    stakeholder = Stakeholder.objects.first()
    assert list(stakeholder.policies.values_list("id", flat=True)) == [policy.id]
