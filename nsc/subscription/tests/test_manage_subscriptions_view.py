from itertools import chain

from django.conf import settings
from django.urls import reverse

import pytest

from ...notify.models import Email
from ..models import Subscription
from ..signer import get_object_signature


pytestmark = pytest.mark.django_db


def test_object_does_not_exist_result_is_not_found(django_app, make_subscription):
    sub = make_subscription()

    url = reverse(
        "subscription:public-manage",
        kwargs={"token": get_object_signature(sub), "pk": sub.id},
    )

    sub.delete()

    assert django_app.get(url, expect_errors=True).status_code == 404


def test_signature_is_incorrect_result_is_not_found(django_app, make_subscription):
    sub1, sub2 = make_subscription(_quantity=2)

    url = reverse(
        "subscription:public-manage",
        kwargs={"token": get_object_signature(sub1), "pk": sub2.id},
    )

    assert django_app.get(url, expect_errors=True).status_code == 404


def test_signature_is_correct_result_is_found(django_app, make_subscription):
    sub = make_subscription()

    url = reverse(
        "subscription:public-manage",
        kwargs={"token": get_object_signature(sub), "pk": sub.id},
    )

    assert django_app.get(url).status_code == 200


def test_subscription_is_updated(django_app, make_subscription, make_policy):
    selected_policies = make_policy(_quantity=3)
    new_selected_policies = make_policy(_quantity=3)
    make_policy(_quantity=3)

    sub = make_subscription(policies=selected_policies)

    url = reverse(
        "subscription:public-manage",
        kwargs={"token": get_object_signature(sub), "pk": sub.id},
    )

    response = django_app.get(url)

    form = response.form
    form["policies"] = [p.id for p in chain(selected_policies, new_selected_policies)]
    response = form.submit("save")

    sub.refresh_from_db()
    assert Subscription.objects.count() == 1
    assert set(sub.policies.values_list("id", flat=True)) == {
        s.id for s in chain(selected_policies, new_selected_policies)
    }
    assert Email.objects.filter(
        address=sub.email,
        template_id=settings.NOTIFY_TEMPLATE_UPDATED_SUBSCRIPTION,
        context={
            "manage_url": response.request.relative_url(
                reverse(
                    "subscription:public-manage",
                    kwargs={"pk": sub.id, "token": get_object_signature(sub)},
                )
            )
        },
    ).exists()
    assert response.location == reverse(
        "subscription:public-complete",
        kwargs={"token": get_object_signature(sub), "pk": sub.id},
    )


def test_subscription_is_deleted(django_app, make_subscription):
    sub = make_subscription()

    url = reverse(
        "subscription:public-manage",
        kwargs={"token": get_object_signature(sub), "pk": sub.id},
    )

    response = django_app.get(url)

    form = response.form
    response = form.submit("delete")

    assert Subscription.objects.count() == 0
    assert Email.objects.filter(
        address=sub.email,
        template_id=settings.NOTIFY_TEMPLATE_UNSUBSCRIBE,
        context={
            "resub_url": response.request.relative_url(
                reverse("subscription:stakeholder-start")
            ),
        },
    ).exists()
    assert response.location == reverse("subscription:public-deleted")
