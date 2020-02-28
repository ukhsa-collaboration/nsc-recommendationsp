import pytest
from model_bakery import baker

from ..models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db


def test_factory_create_policy():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Policy)
    assert isinstance(instance, Policy)


def test_active():
    """
    Test the queryset active() method only returns active policies.
    """
    baker.make(Policy, is_active=True)
    baker.make(Policy, is_active=False)
    expected = [obj.pk for obj in Policy.objects.filter(is_active=True)]
    actual = [obj.pk for obj in Policy.objects.active()]
    assert expected == actual


def test_search_on_name():
    """
    Test the queryset search() method searches the name field.
    """
    baker.make(Policy, name="title with keyword")
    baker.make(Policy, name="other")
    expected = [obj.pk for obj in Policy.objects.filter(name__icontains="with")]
    actual = [obj.pk for obj in Policy.objects.search("with")]
    assert expected == actual


def test_search_on_keywords():
    """
    Test the queryset search() method searches the keywords field.
    """
    baker.make(Policy, name="first", keywords="keyword")
    baker.make(Policy, name="other")
    expected = [obj.pk for obj in Policy.objects.filter(name="first")]
    actual = [obj.pk for obj in Policy.objects.search("keyword")]
    assert expected == actual


def test_search_is_case_insensitive():
    """
    Test the queryset search() method ignores the case of the name or keywords.
    """
    baker.make(Policy, name="first", keywords="KEYWORD")
    baker.make(Policy, name="other")
    expected = [obj.pk for obj in Policy.objects.filter(name="first")]
    actual = [obj.pk for obj in Policy.objects.search("FIRST")]
    assert expected == actual
    actual = [obj.pk for obj in Policy.objects.search("keyword")]
    assert expected == actual


def test_search_on_partial_keywords():
    """
    Test the queryset search() matches part of a keyword.
    """
    baker.make(Policy, name="first", keywords="keyword")
    baker.make(Policy, name="other")
    expected = [obj.pk for obj in Policy.objects.filter(name="first")]
    actual = [obj.pk for obj in Policy.objects.search("key")]
    assert expected == actual


def test_slug_is_set():
    """
    Test the slug field, if not set, is generated from the name field.
    """
    instance = baker.make(Policy, name="The Condition", slug="")
    instance.clean()
    assert instance.slug == "the-condition"


def test_slug_is_not_overwritten():
    """
    Test that once the slug is set it is not overwritten if the name of the
    policy changes. This ensures that any bookmarked pages still work if the
    name is changed at a later time.
    """
    instance = baker.make(Policy, name="The condition", slug="the-condition")
    instance.name = "New name"
    instance.clean()
    assert instance.slug == "the-condition"


def test_condition_markdown_conversion():
    """
    Test the markdown in the condition attribute is converted to HTML when the model is cleaned.
    """
    instance = baker.make(Policy, condition="# Heading", condition_html="")
    instance.clean()
    assert instance.condition_html == '<h1 class="govuk-heading-xl">Heading</h1>'


def test_summary_markdown_conversion():
    """
    Test the markdown in the summary attribute is converted to HTML when the model is cleaned.
    """
    instance = baker.make(Policy, summary="# Heading", summary_html="")
    instance.clean()
    assert instance.summary_html == '<h1 class="govuk-heading-xl">Heading</h1>'
