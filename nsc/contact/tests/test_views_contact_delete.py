from django.urls import reverse

import pytest
from bs4 import BeautifulSoup

from ..models import Contact


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(contact, django_app):
    return django_app.get(reverse("contact:delete", kwargs={"pk": contact.pk}))


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_delete_view(contact, response):
    """
    Test that the delete contact page can be displayed.
    """
    assert response.status == "200 OK"
    assert response.context["object"] == contact


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
    actual = response.form.submit().follow()
    assert actual.request.path == contact.stakeholder.get_detail_url()


def test_contact_deleted(contact, response):
    """
    Test that the contact object is deleted from the database.
    """
    response.form.submit().follow()
    assert not Contact.objects.filter(pk=contact.pk).exists()
