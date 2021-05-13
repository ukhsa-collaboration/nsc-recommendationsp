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
def response(url, erm_user, django_app):
    return django_app.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_delete_view(stakeholder, response):
    """
    Test that the delete stakeholder page can be displayed.
    """
    assert response.status == "200 OK"
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


def test_success_url(response):
    """
    Test deleting an stakeholder returns to the stakeholder list page.
    """
    actual = response.forms[1].submit().follow()
    assert actual.request.path == reverse("stakeholder:list")


def test_stakeholder_deleted(stakeholder, response):
    """
    Test that the stakeholder object is deleted from the database.
    """
    response.forms[1].submit().follow()
    assert not Stakeholder.objects.filter(pk=stakeholder.pk).exists()
