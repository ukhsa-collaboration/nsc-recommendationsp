from itertools import chain

from django.urls import reverse

import pytest

from ..models import Subscription
from ..signer import get_object_signature


pytestmark = pytest.mark.django_db


def test_subscription_start_forwards_to_creation_form(
    django_app, make_subscription, make_policy
):
    selected_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    url = reverse("subscription:public-start")

    response = django_app.get(url)

    form = response.form
    form["policies"] = [s.pk for s in selected_policies]
    response = form.submit()

    assert response.request.path == reverse("subscription:public-subscribe")
    assert set(response.request.GET.getall("policies")) == {
        str(s.pk) for s in selected_policies
    }


def test_emails_dont_match_subscription_isnt_created(
    django_app, make_subscription, make_policy
):
    selected_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    url = reverse("subscription:public-subscribe")
    policies_url_args = "&".join(map(lambda p: f"policies={p.id}", selected_policies))

    response = django_app.get(f"{url}?{policies_url_args}")

    form = response.form
    form["email"] = "foo@example.com"
    form["email_confirmation"] = "bar@example.com"
    form.submit()

    assert not Subscription.objects.exists()


def test_emails_match_subscription_is_created(
    django_app, make_subscription, make_policy
):
    selected_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    url = reverse("subscription:public-subscribe")
    policies_url_args = "&".join(map(lambda p: f"policies={p.id}", selected_policies))

    response = django_app.get(f"{url}?{policies_url_args}")

    form = response.form
    form["email"] = "foo@example.com"
    form["email_confirmation"] = "foo@example.com"
    response = form.submit()

    sub = Subscription.objects.first()
    assert Subscription.objects.count() == 1
    assert sub.email == "foo@example.com"
    assert set(sub.policies.values_list("id", flat=True)) == {
        s.id for s in selected_policies
    }
    assert response.location == reverse(
        "subscription:public-complete",
        kwargs={"token": get_object_signature(sub), "pk": sub.id},
    )


def test_subscription_already_exists_for_email_new_policies_are_added(
    django_app, make_subscription, make_policy
):
    selected_policies = make_policy(_quantity=3)
    new_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    make_subscription(email="foo@example.com", policies=selected_policies)

    url = reverse("subscription:public-subscribe")
    policies_url_args = "&".join(map(lambda p: f"policies={p.id}", new_policies))

    response = django_app.get(f"{url}?{policies_url_args}")

    form = response.form
    form["email"] = "foo@example.com"
    form["email_confirmation"] = "foo@example.com"
    response = form.submit()

    sub = Subscription.objects.first()
    assert Subscription.objects.count() == 1
    assert sub.email == "foo@example.com"
    assert set(sub.policies.values_list("id", flat=True)) == {
        s.id for s in chain(selected_policies, new_policies)
    }
    assert response.location == reverse(
        "subscription:public-complete",
        kwargs={"token": get_object_signature(sub), "pk": sub.id},
    )
