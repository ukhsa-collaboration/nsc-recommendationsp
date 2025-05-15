from django.urls import reverse
from django.utils.translation import gettext

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url(stakeholder):
    return reverse("stakeholder:edit", kwargs={"pk": stakeholder.pk})


@pytest.fixture
def response(url, erm_user, client):
    client.force_login(erm_user)
    return client.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_edit_view(stakeholder, response):
    """
    Test that the stakeholder detail page can be displayed
    """
    assert response.status_code == 200
    assert response.context["stakeholder"] == stakeholder


def test_edit_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_edit_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_back_link(stakeholder, dom):
    """
    Test the back link returns to the list of stakeholders.
    """
    link = dom.find(id="back-link-id")

    assert link["href"] == reverse("stakeholder:detail", kwargs={"pk": stakeholder.pk})

    assert link.text.strip() == gettext("Back")


def test_success_url__next(erm_user, stakeholder, make_policy, client):
    """
    Test saving a contact returns to the stakeholder list page.
    """
    client.force_login(erm_user)
    policy = make_policy()
    stakeholder_edit = reverse("stakeholder:edit", args=(stakeholder.pk,))
    url = f"{stakeholder_edit}?next=/"

    # Build POST data for the edit form.
    post_data = {
        "name": stakeholder.name,
        "is_public": stakeholder.is_public,
        "type": stakeholder.type,
        # Policies formset
        "policies-TOTAL_FORMS": "1",
        "policies-INITIAL_FORMS": "0",
        "policies-MIN_NUM_FORMS": "0",
        "policies-MAX_NUM_FORMS": "1000",
        "policies-0-policy": policy.id,
        # Contacts formset
        "contacts-TOTAL_FORMS": "1",
        "contacts-INITIAL_FORMS": "0",
        "contacts-MIN_NUM_FORMS": "0",
        "contacts-MAX_NUM_FORMS": "1000",
        "contacts-0-name": "Name",
        "contacts-0-email": "name@example.com",
    }

    response = client.post(url, data=post_data, follow=True)
    assert response.request["PATH_INFO"] == "/"
