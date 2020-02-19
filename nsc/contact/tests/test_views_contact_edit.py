from django.urls import reverse

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(contact, django_app):
    return django_app.get(reverse("contact:edit", kwargs={"pk": contact.pk}))


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_edit_view(contact, response):
    """
    Test that the edit contact page can be displayed.
    """
    assert response.status == "200 OK"
    assert response.context["object"] == contact


def test_back_link(contact, dom):
    """
    Test the back link returns to the organisation detail page
    """
    link = dom.find(id="back-link-id")
    organisation = contact.organisation
    assert link["href"] == organisation.get_detail_url()
    assert organisation.name in link.text


def test_success_url(contact, response):
    """
    Test saving a contact returns to the organisation detail page.
    """
    organisation = contact.organisation
    actual = response.form.submit().follow()
    assert actual.request.path == organisation.get_detail_url()
