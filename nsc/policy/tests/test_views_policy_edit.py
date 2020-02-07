import pytest
from model_bakery import baker

from nsc.policy.models import Policy
from nsc.utils.markdown import convert


# All tests require the database
pytestmark = pytest.mark.django_db


def test_edit_view(django_app):
    """
    Test that we edit an instance .
    """
    instance = baker.make(Policy)
    response = django_app.get(instance.get_edit_url())
    assert response.context["policy"] == instance


def test_back_link(django_app):
    """
    Test the back link returns to the detail page.
    """
    instance = baker.make(Policy)
    edit_page = django_app.get(instance.get_admin_url()).click(linkid="edit-link-id")
    next_page = edit_page.click(linkid="back-link-id")
    assert next_page.request.path == instance.get_admin_url()


def test_preview_and_publish(django_app):
    """
    Test the edit view supports preview and publish steps to update the policy.
    """
    instance = baker.make(Policy, condition="# heading", next_review=None)
    edit_form = django_app.get(instance.get_edit_url()).form
    edit_form["next_review"] = "2020"
    edit_form["condition"] = "# updated"
    preview_form = edit_form.submit(name="preview").form
    preview_form.submit(name="publish")
    instance.refresh_from_db()
    assert instance.condition == "# updated"
    assert instance.condition_html == convert("# updated")
