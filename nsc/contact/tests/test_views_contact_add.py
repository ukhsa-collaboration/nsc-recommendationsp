from django.urls import reverse

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url(stakeholder):
    return reverse("contact:add", kwargs={"org_pk": stakeholder.pk})


@pytest.fixture
def response(url, django_app, erm_user):
    return django_app.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_page(response):
    """
    Test that the add contact page can be displayed.
    """
    assert response.status == "200 OK"


def test_page__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_page__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_back_link(stakeholder, dom):
    """
    Test the back link returns to the stakeholder detail page
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == stakeholder.get_detail_url()
    assert stakeholder.name in link.text


def test_success_url(stakeholder, response):
    """
    Test saving a contact returns to the stakeholder detail page.
    """
    form = response.forms[1]
    form["name"] = "Name"
    form["email"] = "john@example.com"
    actual = form.submit().follow()
    assert actual.request.path == stakeholder.get_detail_url()


def test_contact_created(stakeholder, response):
    """
    Test that the contact object is created and added to the stakeholder.
    """
    assert stakeholder.contacts.count() == 0
    form = response.forms[1]
    form["name"] = "Name"
    form["email"] = "john@example.com"
    form.submit().follow()
    assert stakeholder.contacts.count() == 1
