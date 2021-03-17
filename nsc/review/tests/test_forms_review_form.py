import pytest
from model_bakery import baker

from nsc.policy.models import Policy

from ..forms import ReviewForm
from ..models import Review


# All tests require the database
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


def test_name_cannot_be_blank():
    """
    Test that the admin must set the name of the review.
    """
    data = form_for_review(name="")
    form = ReviewForm(data=data)
    assert not form.is_valid()
    assert "name" in form.errors


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
