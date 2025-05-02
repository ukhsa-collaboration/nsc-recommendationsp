from django.urls import reverse
from django.utils.translation import gettext

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url(stakeholder):
    return reverse("stakeholder:edit", kwargs={"pk": stakeholder.pk})


@pytest.fixture
def response(url, erm_user, django_app):
    return django_app.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_edit_view(stakeholder, response):
    """
    Test that the stakeholder detail page can be displayed
    """
    assert response.status == "200 OK"
    assert response.context["stakeholder"] == stakeholder


def test_edit_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_edit_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_back_link(stakeholder, dom):
    """
    Test the back link returns to the list of stakeholders.
    """
    print("DOM", dom)
    link = dom.find(id="back-link-id")

    # assert link is not None
    assert link["href"] == reverse("stakeholder:detail", kwargs={"pk": stakeholder.pk})

    assert link.text.strip() == gettext("Back")


def test_success_url__next(erm_user, stakeholder, make_policy, django_app):
    """
    Test saving a contact returns to the stakeholder list page.
    """
    policy = make_policy()
    stakeholder_edit = reverse("stakeholder:edit", args=(stakeholder.pk,))
    response = django_app.get(f"{stakeholder_edit}?next=/", user=erm_user)
    form = response.forms[1]
    form["policies-0-policy"] = policy.id
    actual = form.submit().follow()
    assert actual.request.path == "/"
