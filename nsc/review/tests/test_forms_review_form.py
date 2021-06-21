import pytest
from model_bakery import baker

from nsc.policy.models import Policy

from ...utils.datetime import get_today
from ..forms import ReviewForm
from ..models import Review


pytestmark = pytest.mark.django_db


def form_for_review(**kwargs):
    data = {
        "name": "Review",
        "review_type": [Review.TYPE.evidence],
        "policies-TOTAL_FORMS": 0,
        "policies-INITIAL_FORMS": 0,
        "policies-MIN_NUM_FORMS": 1,
        "policies-MAX_NUM_FORMS": 1000,
    }
    data.update(kwargs)
    return data


def test_form_configuration():
    """
    Test that the correct model and fields are set in the form.
    """
    assert Review == ReviewForm.Meta.model
    assert "name" in ReviewForm.Meta.fields
    assert "review_type" in ReviewForm.Meta.fields


@pytest.mark.parametrize(
    "policy_names, expected_review_name",
    [
        (["First"], "First {year} review"),
        (["First", "Second"], "First and Second {year} review"),
        (["First", "Second", "Third"], "First, Second and Third {year} review"),
    ],
)
def test_blank_name_is_auto_populated(policy_names, expected_review_name, user):
    """
    Test that the admin must set the name of the review.
    """
    policies = [baker.make(Policy, name=name) for name in policy_names]
    policies_data = {
        "policies-TOTAL_FORMS": len(policies),
        **{f"policies-{idx}-policy": p.id for idx, p in enumerate(policies)},
    }

    data = form_for_review(name="", **policies_data)
    form = ReviewForm(instance=Review(user=user), data=data)
    assert form.is_valid()
    review = form.save()
    assert review.name == expected_review_name.format(year=get_today().year)


def test_review_type_cannot_be_none():
    """
    Test that the admin must select which type of review it is.
    """
    data = form_for_review(review_type=None)
    form = ReviewForm(data=data)
    assert not form.is_valid()
    assert "review_type" in form.errors


def test_policy_list_cannot_be_empty():
    """
    Test that the admin must select at least one condition.
    """
    data = form_for_review()
    form = ReviewForm(data=data)
    assert not form.is_valid()
    assert len(form.policy_formset.non_form_errors()) > 0


def test_policy_list_with_invalid_policy():
    """
    Test that if a condition does not exist then an error is reported.
    """
    data = form_for_review(**{"policies-0-policy": 42, "policies-TOTAL_FORMS": 1})
    form = ReviewForm(data=data)
    assert not form.is_valid()
    assert "policy" in form.policy_formset.errors[0]


def test_review_is_created(erm_user):
    """
    Test saving the form creates a new review.
    """
    policy = baker.make(Policy, name="name", slug="name")
    data = form_for_review(
        **{"policies-0-policy": policy.pk, "policies-TOTAL_FORMS": 1}
    )
    form = ReviewForm(data=data, instance=Review(user=erm_user))
    instance = form.save()
    assert instance.name == data["name"]
    assert instance.review_type == data["review_type"]
    policies = [obj.pk for obj in instance.policies.all()]
    assert policies == [policy.pk]
