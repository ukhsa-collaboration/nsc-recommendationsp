from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.document.models import DocumentPolicy
from nsc.policy.models import Policy
from nsc.utils.markdown import convert


# All tests require the database
pytestmark = pytest.mark.django_db


def test_detail__back_link(erm_user, django_app):
    """
    Test the back link returns to the detail page.
    """
    instance = baker.make(Policy)
    detail_page = django_app.get(
        reverse("policy:archive:detail", args=(instance.slug,)), user=erm_user
    )
    next_page = detail_page.click(linkid="back-link-id")
    assert next_page.request.path == instance.get_admin_url()


def test_upload__back_link(erm_user, django_app):
    """
    Test the back link returns to the detail page.
    """
    instance = baker.make(Policy)
    upload_page = django_app.get(
        reverse("policy:archive:upload", args=(instance.slug,)), user=erm_user
    )
    next_page = upload_page.click(linkid="back-link-id")
    assert next_page.request.path == reverse(
        "policy:archive:detail", args=(instance.slug,)
    )


def test_update__back_link(erm_user, django_app):
    """
    Test the back link returns to the detail page.
    """
    instance = baker.make(Policy)
    update_page = django_app.get(
        reverse("policy:archive:update", args=(instance.slug,)), user=erm_user
    )
    next_page = update_page.click(linkid="back-link-id")
    assert next_page.request.path == reverse(
        "policy:archive:upload", args=(instance.slug,)
    )


def test_detail_view(erm_user, django_app):
    """
    Test that we can view an instance via the detail view.
    """
    instance = baker.make(Policy)
    response = django_app.get(
        reverse("policy:archive:detail", args=(instance.slug,)), user=erm_user
    )
    assert response.context["policy"] == instance


def test_detail_view__no_user(test_access_no_user):
    instance = baker.make(Policy)
    test_access_no_user(url=reverse("policy:archive:detail", args=(instance.slug,)))


def test_detail_view__incorrect_permission(test_access_forbidden):
    instance = baker.make(Policy)
    test_access_forbidden(url=reverse("policy:archive:detail", args=(instance.slug,)))


def test_upload_view__create_document(erm_user, minimal_pdf, django_app):
    """
    Test that we can create a document via the upload view.
    """

    instance = baker.make(Policy, slug="abc")
    upload_url = reverse("policy:archive:upload", args=(instance.slug,))
    form = django_app.get(upload_url, user=erm_user).forms[2]
    form["document-TOTAL_FORMS"] = 1
    form["document-0-name"] = "Some name"
    form["document-0-upload"] = (
        "document.pdf",
        minimal_pdf.encode(),
        "application/pdf",
    )
    response = form.submit().follow()
    document_policy = DocumentPolicy.objects.filter(policy=instance).first()
    document = document_policy.document
    assert response.status == "200 OK"
    assert response.request.path == upload_url
    assert document is not None
    assert document.file_exists()
    assert document.name == "Some name"
    assert document_policy.policy == instance
    assert document_policy.source == "archive"


def test_upload_view__no_user(test_access_no_user):
    instance = baker.make(Policy)
    test_access_no_user(url=reverse("policy:archive:upload", args=(instance.slug,)))


def test_upload_view__incorrect_permission(test_access_forbidden):
    instance = baker.make(Policy)
    test_access_forbidden(url=reverse("policy:archive:upload", args=(instance.slug,)))


def test_update_view__preview(erm_user, django_app):
    """
    Test the preview page.
    """
    instance = baker.make(Policy, archived_reason="# heading")

    update_page = django_app.get(
        reverse("policy:archive:update", args=(instance.slug,)), user=erm_user
    )
    update_form = update_page.forms[2]
    update_form["archived_reason"] = "# updated"

    preview_page = update_form.submit(name="preview")
    preview_form = preview_page.forms[1]
    assert preview_form["archived_reason"].attrs["type"] == "hidden"
    assert preview_form["archived_reason"].value == "# updated"
    assert preview_page.context.get("preview") == "preview"
    assert preview_page.context.get("publish") is None


def test_update_view__published(erm_user, django_app):
    """
    Test the preview page.
    """
    instance = baker.make(Policy, archived_reason="# heading", archived=False)

    update_page = django_app.get(
        reverse("policy:archive:update", args=(instance.slug,)), user=erm_user
    )
    update_form = update_page.forms[2]
    update_form["archived_reason"] = "# updated"

    preview_page = update_form.submit(name="preview")

    instance.refresh_from_db()
    assert instance.archived_reason == "# heading"

    preview_form = preview_page.forms[1]
    result = preview_form.submit(name="publish")

    assert result.status == "302 Found"
    assert result.url == reverse("policy:archive:complete", args=(instance.slug,))

    instance.refresh_from_db()
    assert instance.archived
    assert instance.archived_reason == "# updated"
    assert instance.archived_reason_html == convert("# updated")


def test_update_view__no_user(test_access_no_user):
    instance = baker.make(Policy)
    test_access_no_user(url=reverse("policy:archive:update", args=(instance.slug,)))


def test_update_view__incorrect_permission(test_access_forbidden):
    instance = baker.make(Policy)
    test_access_forbidden(url=reverse("policy:archive:update", args=(instance.slug,)))


def test_complete_view(erm_user, django_app):
    instance = baker.make(Policy, archived=True)
    response = django_app.get(
        reverse("policy:archive:complete", args=(instance.slug,)), user=erm_user
    )
    assert response.context["policy"] == instance


def test_complete_view__no_user(test_access_no_user):
    instance = baker.make(Policy, archived=True)
    test_access_no_user(url=reverse("policy:archive:complete", args=(instance.slug,)))


def test_complete_view__incorrect_permission(test_access_forbidden):
    instance = baker.make(Policy, archived=True)
    test_access_forbidden(url=reverse("policy:archive:complete", args=(instance.slug,)))
