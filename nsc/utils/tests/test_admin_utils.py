"""
The admin utils module, nsc.utils.admin, is a collection of utility
functions that is used to get the Django Admin view so they can be
smoke tested - essentially is the page displayed with no errors.
"""
from django.contrib.admin import site
from django.contrib.auth import get_user_model

import pytest

from nsc.utils import admin as utils


# All tests require the database
pytestmark = pytest.mark.django_db


def test_get_add_url():
    assert "/admin/auth/user/add/" == utils.get_add_url(get_user_model())


def test_get_change_url(admin_user):
    expected = "/admin/auth/user/%s/change/" % admin_user.pk
    assert expected == utils.get_change_url(admin_user)


def test_get_delete_url(admin_user):
    expected = "/admin/auth/user/%s/delete/" % admin_user.pk
    assert expected == utils.get_delete_url(admin_user)


def test_get_changelist_url():
    assert "/admin/auth/user/" == utils.get_changelist_url(get_user_model())


def test_get_models():
    names = [model._meta.object_name for model in utils.get_models(site)]
    assert "User" in names
    assert "Group" in names


def test_get_add_models(admin_user):
    names = [
        model._meta.object_name for model in utils.get_add_models(site, admin_user)
    ]
    assert "User" in names
    assert "Group" in names


def test_get_change_models(admin_user):
    names = [
        model._meta.object_name for model in utils.get_change_models(site, admin_user)
    ]
    assert "User" in names
    assert "Group" in names


def test_get_delete_models(admin_user):
    names = [
        model._meta.object_name for model in utils.get_change_models(site, admin_user)
    ]
    assert "User" in names
    assert "Group" in names
