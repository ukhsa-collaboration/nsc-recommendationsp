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


def test_success_url__next(stakeholder, make_policy, django_app):
    """
    Test saving a contact returns to the stakeholder list page.
    """
    policy = make_policy()
    stakeholder_edit = reverse("stakeholder:edit", args=(stakeholder.pk,))
    policy_edit = reverse("policy:edit", args=(policy.slug,))
    response = django_app.get(f"{stakeholder_edit}?next={policy_edit}")
    form = response.form
    form["policies-0-policy"] = policy.id
    actual = form.submit().follow()
    assert actual.request.path == policy_edit
