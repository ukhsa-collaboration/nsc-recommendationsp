from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(organisation, django_app):
    return django_app.get(
        reverse("organisation:detail", kwargs={"pk": organisation.pk})
    )


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_detail_view(organisation, response):
    """
    Test that the Organisation detail page can be displayed
    """
    assert response.status == "200 OK"
    assert response.context["organisation"] == organisation


def test_back_link(dom):
    """
    Test the back link returns to the list of organisations.
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == reverse("organisation:list")
    assert link.text.strip() == _("Back to stakeholders")
