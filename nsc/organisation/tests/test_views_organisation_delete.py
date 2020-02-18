from django.urls import reverse

import pytest
from bs4 import BeautifulSoup

from ..models import Organisation


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(organisation, django_app):
    return django_app.get(
        reverse("organisation:delete", kwargs={"pk": organisation.pk})
    )


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_delete_view(organisation, response):
    """
    Test that the delete organisation page can be displayed.
    """
    assert response.status == "200 OK"
    assert response.context["object"] == organisation


def test_back_link(organisation, dom):
    """
    Test the back link returns to the organisation detail page
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == organisation.get_detail_url()
    assert organisation.name in link.text


def test_success_url(response):
    """
    Test deleting an organisation returns to the organisation list page.
    """
    actual = response.form.submit().follow()
    assert actual.request.path == reverse("organisation:list")


def test_organisation_deleted(organisation, response):
    """
    Test that the organisation object is deleted from the database.
    """
    response.form.submit().follow()
    assert not Organisation.objects.filter(pk=organisation.pk).exists()
