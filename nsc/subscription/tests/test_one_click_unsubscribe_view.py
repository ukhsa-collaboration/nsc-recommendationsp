from django.test import Client
from django.urls import reverse

import pytest

from ..models import Subscription
from ..signer import get_object_signature


pytestmark = pytest.mark.django_db


def _url(sub):
    return reverse(
        "subscription:one-click-unsubscribe",
        kwargs={"pk": sub.pk, "token": get_object_signature(sub)},
    )


def test_post_with_valid_token_deletes_subscription(make_subscription):
    sub = make_subscription()
    client = Client()
    response = client.post(_url(sub))
    assert response.status_code == 200
    assert not Subscription.objects.filter(pk=sub.pk).exists()


def test_post_with_invalid_token_returns_404(make_subscription):
    sub = make_subscription()
    client = Client()
    url = reverse(
        "subscription:one-click-unsubscribe",
        kwargs={"pk": sub.pk, "token": "invalid-token"},
    )
    response = client.post(url)
    assert response.status_code == 404
    assert Subscription.objects.filter(pk=sub.pk).exists()


def test_post_with_nonexistent_subscription_returns_404():
    client = Client()
    url = reverse(
        "subscription:one-click-unsubscribe",
        kwargs={"pk": 99999, "token": "doesnt-matter"},
    )
    response = client.post(url)
    assert response.status_code == 404


def test_get_returns_405(make_subscription):
    sub = make_subscription()
    client = Client()
    response = client.get(_url(sub))
    assert response.status_code == 405
    assert Subscription.objects.filter(pk=sub.pk).exists()
