from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import pytest
from bs4 import BeautifulSoup

from nsc.contact.models import Contact
from nsc.organisation.models import Organisation


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(django_app):
    return django_app.get(reverse("organisation:add"))


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_add_view(response):
    """
    Test that the add organisation page can be displayed.
    """
    assert response.status == "200 OK"


def test_back_link(dom):
    """
    Test the back link returns to the organisation list page
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == reverse("organisation:list")
    assert link.text.strip() == _("Back to stakeholders")


def test_success_url(response):
    """
    Test saving a contact returns to the organisation list page.
    """
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    actual = form.submit().follow()
    assert actual.request.path == reverse("organisation:list")


def test_organisation_created(response):
    """
    Test that the organisation object is created.
    """
    assert Organisation.objects.count() == 0
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form.submit()
    assert Organisation.objects.count() == 1


def test_contact_created(response):
    """
    Test that the organisation object is created.
    """
    assert Contact.objects.count() == 0
    form = response.form
    form["name"] = "Name"
    form["is_public"] = True
    form["contacts-0-name"] = "Name"
    form["contacts-0-email"] = "name@example.com"
    form.submit()
    assert Contact.objects.count() == 1
