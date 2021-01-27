from django.urls import reverse
from django.utils.translation import ugettext

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(stakeholder, django_app):
    return django_app.get(reverse("stakeholder:edit", kwargs={"pk": stakeholder.pk}))


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_edit_view(stakeholder, response):
    """
    Test that the stakeholder detail page can be displayed
    """
    assert response.status == "200 OK"
    assert response.context["stakeholder"] == stakeholder


def test_back_link(stakeholder, dom):
    """
    Test the back link returns to the list of stakeholders.
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == reverse("stakeholder:detail", kwargs={"pk": stakeholder.pk})
    assert link.text.strip() == ugettext("Back to %s" % stakeholder.name)
