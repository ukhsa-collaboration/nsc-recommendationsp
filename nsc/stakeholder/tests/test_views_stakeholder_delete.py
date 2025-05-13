from urllib.parse import urlparse

from django.urls import reverse

import pytest
from bs4 import BeautifulSoup

from ..models import Stakeholder


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url(stakeholder):
    return reverse("stakeholder:delete", kwargs={"pk": stakeholder.pk})


@pytest.fixture
def response(url, erm_user, client):
    client.force_login(erm_user)
    return client.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_delete_view(stakeholder, response):
    """
    Test that the delete stakeholder page can be displayed.
    """
    assert response.status_code == 200
    assert response.context["object"] == stakeholder


def test_delete_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_delete_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_back_link(stakeholder, dom):
    """
    Test the back link returns to the stakeholder detail page
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == stakeholder.get_detail_url()
    assert stakeholder.name in link.text


def test_success_url(response, client, stakeholder):
    """
    Test deleting an stakeholder returns to the stakeholder list page.
    """
    # client.force_login(erm_user)
    url = reverse("stakeholder:delete", kwargs={"pk": stakeholder.pk})
    response = client.post(url)

    # Strip fragment and compare only path
    parsed_url = urlparse(response.url)
    assert parsed_url.path == reverse("stakeholder:list")


def test_stakeholder_deleted(stakeholder, client, response):
    """
    Test that the stakeholder object is deleted from the database.
    """
    # client.force_login(erm_user)
    url = reverse("stakeholder:delete", kwargs={"pk": stakeholder.pk})
    client.post(url)

    assert not Stakeholder.objects.filter(pk=stakeholder.pk).exists()
