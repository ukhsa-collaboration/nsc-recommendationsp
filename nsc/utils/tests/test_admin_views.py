"""
Basic smoke tests for admin views
"""
from django.contrib import admin

import pytest
from model_bakery import baker

from nsc.condition.models import Condition
from nsc.policy.models import Policy
from nsc.utils.admin import (
    get_add_models,
    get_add_url,
    get_change_models,
    get_change_url,
    get_changelist_url,
    get_delete_models,
    get_delete_url,
    get_models,
)


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_test_instances(db):
    return {"Condition": baker.make(Condition), "Policy": baker.make(Policy)}


def test_changelist_views(admin_client):
    for model in get_models(admin.site):
        assert admin_client.get(get_changelist_url(model)).status_code == 200


def test_add_views(admin_user, admin_client):
    for model in get_add_models(admin.site, admin_user):
        assert admin_client.get(get_add_url(model)).status_code == 200


def test_change_views(admin_user, admin_client, admin_test_instances):
    models = [
        model
        for model in get_change_models(admin.site, admin_user)
        if model.__name__ in admin_test_instances
    ]

    for model in models:
        instance = admin_test_instances[model.__name__]
        assert admin_client.get(get_change_url(instance)).status_code == 200


def test_delete_views(admin_user, admin_client, admin_test_instances):
    models = [
        model
        for model in get_delete_models(admin.site, admin_user)
        if model.__name__ in admin_test_instances
    ]

    for model in models:
        instance = admin_test_instances[model.__name__]
        assert admin_client.get(get_delete_url(instance)).status_code == 200
