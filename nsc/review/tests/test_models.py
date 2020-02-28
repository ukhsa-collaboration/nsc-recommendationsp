import pytest
from model_bakery import baker

from ..models import Review


# All tests require the database
pytestmark = pytest.mark.django_db


def test_factory_create_policy():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Review)
    assert isinstance(instance, Review)


def test_slug_is_set():
    """
    Test the slug field, if not set, is generated from the name field.
    """
    instance = baker.make(Review, name="The Review", slug="")
    instance.clean()
    assert instance.slug == "the-review"


def test_slug_is_not_overwritten():
    """
    Test that once the slug is set it is not overwritten if the name of the
    policy changes. This ensures that any bookmarked pages still work if the
    name is changed at a later time.
    """
    instance = baker.make(Review, name="The Review", slug="the-review")
    instance.name = "New name"
    instance.clean()
    assert instance.slug == "the-review"


def test_summary_markdown_conversion():
    """
    Test the markdown in the summary attribute is converted to HTML when the model is cleaned.
    """
    instance = baker.make(Review, summary="# Heading", summary_html="")
    instance.clean()
    assert instance.summary_html == '<h1 class="govuk-heading-xl">Heading</h1>'
