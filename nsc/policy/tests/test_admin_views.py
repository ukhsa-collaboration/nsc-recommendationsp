from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.policy.models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db


def test_changelist_view(admin_client):
    url = reverse("admin:policy_policy_changelist")
    assert admin_client.get(url).status_code == 200


def test_add_view(admin_client):
    url = reverse("admin:policy_policy_add")
    assert admin_client.get(url).status_code == 200


def test_change_view(admin_client):
    instance = baker.make(Policy)
    url = reverse("admin:policy_policy_delete", args=(instance.pk,))
    assert admin_client.get(url).status_code == 200


def test_delete_view(admin_client):
    instance = baker.make(Policy)
    url = reverse("admin:policy_policy_delete", args=(instance.pk,))
    assert admin_client.get(url).status_code == 200
