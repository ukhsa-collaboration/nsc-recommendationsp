from django.urls import reverse

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(organisation, set_session_variable, django_app):
    set_session_variable("organisation", organisation.pk)
    return django_app.get(reverse("contact:add"))


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_page(response):
    """
    Test that the add contact page can be displayed.
    """
    assert response.status == "200 OK"


def test_back_link(organisation, dom):
    """
    Test the back link returns to the organisation detail page
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == organisation.get_detail_url()
    assert organisation.name in link.text


def test_success_url(organisation, response):
    """
    Test saving a contact returns to the organisation detail page.
    """
    form = response.form
    form["name"] = "Name"
    form["email"] = "john@example.com"
    actual = form.submit().follow()
    assert actual.request.path == organisation.get_detail_url()


def test_contact_created(organisation, response):
    """
    Test that the contact object is created and added to the organisation.
    """
    assert organisation.contacts.count() == 0
    form = response.form
    form["name"] = "Name"
    form["email"] = "john@example.com"
    form.submit().follow()
    assert organisation.contacts.count() == 1
