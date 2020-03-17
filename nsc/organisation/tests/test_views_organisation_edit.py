from django.urls import reverse
from django.utils.translation import ugettext

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(organisation, django_app):
    return django_app.get(
        reverse("organisation:edit", kwargs={"pk": organisation.pk, "field": "name"})
    )


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_edit_view(organisation, response):
    """
    Test that the Organisation detail page can be displayed
    """
    assert response.status == "200 OK"
    assert response.context["organisation"] == organisation


def test_back_link(organisation, dom):
    """
    Test the back link returns to the list of organisations.
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == reverse(
        "organisation:detail", kwargs={"pk": organisation.pk}
    )
    assert link.text.strip() == ugettext("Back to %s" % organisation.name)
