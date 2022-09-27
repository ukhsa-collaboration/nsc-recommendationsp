from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url(stakeholder):
    return reverse("stakeholder:detail", kwargs={"pk": stakeholder.pk})


@pytest.fixture
def response(url, erm_user, django_app):
    return django_app.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_detail_view(stakeholder, response):
    """
    Test that the stakeholder detail page can be displayed
    """
    assert response.status == "200 OK"
    assert response.context["stakeholder"] == stakeholder


def test_detail_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_detail_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_back_link(dom):
    """
    Test the back link returns to the list of stakeholders.
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == reverse("stakeholder:list")
    assert link.text.strip() == _("Back to stakeholders")
