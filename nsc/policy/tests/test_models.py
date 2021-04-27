from django.core.cache import cache

import pytest
from dateutil.relativedelta import relativedelta
from model_bakery import baker

from nsc.review.models import Review
from nsc.utils.datetime import from_today, get_today

from ..models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db


def relative_date(**kwargs):
    return get_today() + relativedelta(**kwargs)


def test_factory_create_policy():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Policy)
    assert isinstance(instance, Policy)


def test_active(make_policy):
    """
    Test the queryset active() method only returns active policies.
    """
    make_policy(is_active=True)
    make_policy(is_active=False)
    expected = [obj.pk for obj in Policy.objects.filter(is_active=True)]
    actual = [obj.pk for obj in Policy.objects.active()]
    assert expected == actual


def test_overdue(make_policy):
    """
    Test the queryset overdue() method includes records where next_review is in the past.
    """
    make_policy(next_review=relative_date(months=+1))
    make_policy(next_review=relative_date(months=-1))
    expected = [obj.pk for obj in Policy.objects.filter(next_review__lt=get_today())]
    actual = [obj.pk for obj in Policy.objects.overdue()]
    assert expected == actual


def test_yesterday_is_overdue(make_policy):
    """
    Test the queryset overdue() method does not include policies with a next
    review date of today.
    """
    make_policy(next_review=get_today())
    instance = make_policy(next_review=get_today() - relativedelta(days=1))
    actual = [obj.pk for obj in Policy.objects.overdue()]
    assert [instance.pk] == actual


def test_no_review_is_overdue(make_policy):
    """
    Test the queryset overdue() method includes records where next_review is not set.
    """
    make_policy(next_review=get_today())
    instance = make_policy(next_review=None)
    actual = [obj.pk for obj in Policy.objects.overdue()]
    assert [instance.pk] == actual


def test_today_is_not_overdue(make_policy):
    """
    Test the queryset overdue() method does not include policies with a next
    review date of today.
    """
    make_policy(next_review=get_today())
    actual = [obj.pk for obj in Policy.objects.overdue()]
    assert [] == actual


def test_upcoming(make_policy):
    """
    Test the queryset upcoming method() includes records where the next
    review is scheduled anytime in the next twelve months.
    """
    make_policy(next_review=relative_date(months=+11))
    make_policy(next_review=relative_date(days=-1))
    expected = [obj.pk for obj in Policy.objects.filter(next_review__gte=get_today())]
    actual = [obj.pk for obj in Policy.objects.upcoming()]
    assert expected == actual


def test_today_is_upcoming(make_policy):
    """
    Test the queryset upcoming() method includes policies with a next
    review date of today.
    """
    make_policy(next_review=get_today())
    yesterday = get_today() - relativedelta(days=1)
    expected = [obj.pk for obj in Policy.objects.filter(next_review__gt=yesterday)]
    actual = [obj.pk for obj in Policy.objects.upcoming()]
    assert expected == actual


def test_yesterday_is_not_upcoming(make_policy):
    """
    Test the queryset upcoming() method excludd policies with a next
    review date in the past.
    """
    make_policy(next_review=get_today() - relativedelta(days=1))
    actual = [obj.pk for obj in Policy.objects.upcoming()]
    assert [] == actual


def test_upcoming_limit(make_policy):
    """
    Test the queryset upcoming method() only includes records where the next
    review date is within the next twelve months.
    """
    make_policy(next_review=relative_date(years=1))
    actual = [obj.pk for obj in Policy.objects.upcoming()]
    assert [] == actual


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


def test_archived_reason_markdown_conversion():
    """
    Test the markdown in the archived_reason attribute is converted to HTML when the model is cleaned.
    """
    instance = baker.make(Policy, archived_reason="# Heading", archived_reason_html="")
    instance.clean()
    assert instance.archived_reason_html == '<h1 class="govuk-heading-xl">Heading</h1>'


@pytest.mark.parametrize(
    "start,end,count",
    [
        (None, None, 0),  # valid: review in pre-consultation
        (from_today(+1), from_today(+30), 0),  # valid: consultation dates set
        (get_today(), from_today(+7), 1),  # valid: consultation period opens today
        (from_today(-30), get_today(), 1),  # valid: consultation period closes today
        (from_today(-30), from_today(-1), 0),  # valid: review in post-consultation
        (from_today(+1), None, 0),  # error: pre-consultation but only start date set
        (get_today(), None, 0),  # error: consultation opens but only start date set
        (None, from_today(-1), 0),  # error: post-consultation but only end date set
    ],
)
def test_open_for_comments(start, end, count):
    """
    Test the queryset method open_for_comments only returns Policy objects which are
    currently in review and are in the consultation phase.
    """
    policy = baker.make(Policy)
    review = baker.make(Review, consultation_start=start, consultation_end=end)
    policy.reviews.add(review)
    actual = Policy.objects.open_for_comments().count()
    assert count == actual


@pytest.mark.parametrize(
    "start,end,count",
    [
        (None, None, 1),  # valid: review in pre-consultation
        (from_today(+1), from_today(+30), 1),  # valid: consultation dates set
        (get_today(), from_today(+7), 0),  # valid: consultation period opens today
        (from_today(-30), get_today(), 0),  # valid: consultation period closes today
        (from_today(-30), from_today(-1), 1),  # valid: review in post-consultation
        (from_today(+1), None, 1),  # error: pre-consultation but only start date set
        (get_today(), None, 1),  # error: consultation opens but only start date set
        (None, from_today(-1), 1),  # error: post-consultation but only end date set
    ],
)
def test_closed_for_comments(start, end, count):
    """
    Test the queryset method closed_for_comments excludes Policy objects which are
    currently in review and are in the consultation phase.
    """
    policy = baker.make(Policy)
    review = baker.make(Review, consultation_start=start, consultation_end=end)
    policy.reviews.add(review)
    actual = Policy.objects.closed_for_comments().count()
    assert count == actual


@pytest.mark.parametrize(
    "start,end,count",
    [
        (from_today(+1), from_today(+30), 0),
        (get_today(), from_today(+7), 1),
        (from_today(-30), from_today(-1), 0),
        (from_today(-30), from_today(-1), 0),
    ],
)
def test_prefetch_reviews_in_consultation(start, end, count):
    """
    Test the queryset method prefetch_reviews_in_consultation annotates Policy
    objects with a review if there is currently one in the consultation phase.
    """
    policy = baker.make(Policy)
    review = baker.make(Review, consultation_start=start, consultation_end=end)
    policy.reviews.add(review)
    actual = Policy.objects.prefetch_reviews_in_consultation().first()
    assert len(actual.reviews_in_consultation) == count


def test_policy_is_saved___cache_is_cleared(make_policy):
    cache.set("foo", "bar")

    make_policy()

    assert cache.get("foo") is None


def test_policy_is_deleted___cache_is_cleared(make_policy):
    policy = make_policy()

    cache.set("foo", "bar")

    policy.delete()

    assert cache.get("foo") is None
