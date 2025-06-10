from django.urls import reverse

import pytest
from bs4 import BeautifulSoup

from ..models import Contact


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url(contact):
    return reverse("contact:delete", kwargs={"pk": contact.pk})


@pytest.fixture
def response(url, django_app, erm_user):
    return django_app.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_delete_view(contact, response):
    """
    Test that the delete contact page can be displayed.
    """
    assert response.status == "200 OK"
    assert response.context["object"] == contact


def test_delete_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_delete_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_back_link(contact, dom):
    """
    Test the back link returns to the stakeholder detail page
    """
    link = dom.find(id="back-link-id")
    stakeholder = contact.stakeholder
    assert link["href"] == stakeholder.get_detail_url()
    assert stakeholder.name in link.text


def test_success_url(contact, response):
    """
    Test deleting a contact returns to the stakeholder detail page.
    """
    actual = response.forms[2].submit().follow()
    assert actual.request.path == contact.stakeholder.get_detail_url()


def test_contact_deleted(contact, response):
    """
    Test that the contact object is deleted from the database.
    """
    response.forms[2].submit().follow()
    assert not Contact.objects.filter(pk=contact.pk).exists()
