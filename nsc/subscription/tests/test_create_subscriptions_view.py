from itertools import chain
from urllib.parse import parse_qs, urljoin, urlparse

from django.conf import settings
from django.urls import reverse

import pytest

from ...notify.models import Email
from ..models import Subscription
from ..signer import get_object_signature


pytestmark = pytest.mark.django_db


def test_subscription_start_forwards_to_creation_form(
    client, make_subscription, make_policy
):
    selected_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    url = reverse("subscription:public-start")

    response = client.get(url)

    form = response.forms[1]
    form["policies"] = [s.pk for s in selected_policies]
    response = form.submit("save")

    redirect = urlparse(response.location)
    assert redirect.path == reverse("subscription:public-subscribe")
    assert set(parse_qs(redirect.query)["policies"]) == {
        str(s.pk) for s in selected_policies
    }


def test_emails_dont_match_subscription_isnt_created(
    client, make_subscription, make_policy
):
    selected_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    url = reverse("subscription:public-subscribe")
    policies_url_args = "&".join(map(lambda p: f"policies={p.id}", selected_policies))

    response = client.get(f"{url}?{policies_url_args}")

    form = response.forms[1]
    form["email"] = "foo@example.com"
    form["email_confirmation"] = "bar@example.com"
    form.submit()

    assert not Subscription.objects.exists()


def test_emails_match_subscription_is_created(client, make_subscription, make_policy):
    selected_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    url = reverse("subscription:public-subscribe")
    policies_url_args = "&".join(map(lambda p: f"policies={p.id}", selected_policies))

    response = client.get(f"{url}?{policies_url_args}")

    form = response.forms[1]
    form["email"] = "foo@example.com"
    form["email_confirmation"] = "foo@example.com"
    response = form.submit()

    sub = Subscription.objects.first()
    assert Subscription.objects.count() == 1
    assert sub.email == "foo@example.com"
    assert set(sub.policies.values_list("id", flat=True)) == {
        s.id for s in selected_policies
    }
    assert Email.objects.filter(
        address=sub.email,
        template_id=settings.NOTIFY_TEMPLATE_SUBSCRIBED,
        context={
            "policy list": "\n".join(
                f"* {p.name}"
                for p in sorted(selected_policies, key=lambda p: p.name.lower())
            ),
            "manage subscription url": urljoin(
                response.request.host_url, sub.management_url
            ),
        },
    ).exists()
    assert (
        response.location
        == reverse(
            "subscription:public-complete",
            kwargs={"token": get_object_signature(sub), "pk": sub.id},
        )
        + "#"
    )


def test_subscription_already_exists_for_email_new_policies_are_added(
    client, make_subscription, make_policy
):
    selected_policies = make_policy(_quantity=3)
    new_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    make_subscription(email="foo@example.com", policies=selected_policies)

    url = reverse("subscription:public-subscribe")
    policies_url_args = "&".join(map(lambda p: f"policies={p.id}", new_policies))

    response = client.get(f"{url}?{policies_url_args}")

    form = response.context['form']

    data = {
        'email': 'foo@example.com',
        'email_confirmation': 'foo@example.com',
        'policies': [p.id for p in selected_policies] + [p.id for p in new_policies]
    }
    response = client.post(url, data=data)

    sub = Subscription.objects.first()
    assert Subscription.objects.count() == 1
    assert sub.email == "foo@example.com"
    assert set(sub.policies.values_list("id", flat=True)) == {
        s.id for s in chain(selected_policies, new_policies)
    }
    assert (
        response.url
        == reverse(
            "subscription:public-complete",
            kwargs={"token": get_object_signature(sub), "pk": sub.id},
        )
        + "#"
    )
