import pytest
from dateutil.utils import today
from model_bakery import baker

from nsc.policy.models import Policy
from nsc.utils.markdown import convert


# All tests require the database
pytestmark = pytest.mark.django_db


def test_edit_view(erm_user, django_app):
    """
    Test that we edit an instance.
    """
    instance = baker.make(Policy)
    response = django_app.get(instance.get_edit_url(), user=erm_user)
    assert response.context["policy"] == instance


def test_edit_view__no_user(test_access_no_user):
    instance = baker.make(Policy)
    test_access_no_user(url=instance.get_edit_url())


def test_edit_view__incorrect_permission(test_access_forbidden):
    instance = baker.make(Policy)
    test_access_forbidden(url=instance.get_edit_url())


def test_back_link(erm_user, django_app):
    """
    Test the back link returns to the detail page.
    """
    instance = baker.make(Policy)
    edit_page = django_app.get(instance.get_admin_url(), user=erm_user).click(
        linkid="edit-link-id"
    )
    next_page = edit_page.click(linkid="back-link-id")
    assert next_page.request.path == instance.get_admin_url()


def test_preview_page(erm_user, django_app):
    """
    Test the preview page.

    The preview page is just the edit page redisplayed with the updated
    values rendered in the same form as the details page and the form
    fields are hidden.
    """
    instance = baker.make(Policy, condition="# heading", next_review=None)
    year = str(today().year + 1)

    edit_page = django_app.get(instance.get_edit_url(), user=erm_user)
    edit_form = edit_page.forms[1]
    edit_form["next_review"] = year
    edit_form["condition_type"] = Policy.CONDITION_TYPES.general
    edit_form["ages"] = [Policy.AGE_GROUPS.antenatal]
    edit_form["condition"] = "# updated"

    preview_page = edit_form.submit(name="preview")
    preview_form = preview_page.forms[1]
    assert preview_form["next_review"].attrs["type"] == "hidden"
    assert preview_form["next_review"].value == year
    assert preview_form["condition"].attrs["type"] == "hidden"
    assert preview_form["condition"].value == "# updated"
    assert preview_page.context.get("preview") == "preview"
    assert preview_page.context.get("publish") is None


def test_changes_are_published(erm_user, django_app):
    """
    Test the policy is updated when the changes are published.
    """
    instance = baker.make(Policy, condition="# heading", next_review=None)

    edit_page = django_app.get(instance.get_edit_url(), user=erm_user)
    edit_form = edit_page.forms[1]
    edit_form["next_review"] = today().year
    edit_form["condition_type"] = Policy.CONDITION_TYPES.general
    edit_form["ages"] = [Policy.AGE_GROUPS.antenatal]
    edit_form["condition"] = "# updated"

    preview_page = edit_form.submit(name="preview")

    instance.refresh_from_db()
    assert instance.condition == "# heading"

    preview_form = preview_page.forms[1]
    preview_form.submit(name="publish")

    instance.refresh_from_db()
    assert instance.condition == "# updated"
    assert instance.condition_html == convert("# updated")
