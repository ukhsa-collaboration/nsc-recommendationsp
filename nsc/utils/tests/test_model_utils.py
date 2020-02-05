"""
The model utils module, nsc.utils.models, is a collection of utility
functions that process the metadata of Django apps and models. Since
this sometimes changes with new releases the tests here are used to
identify any problems more easily than debugging the tests that use
the functions.
"""
from django.contrib.auth import get_user_model
from django.db import models

import pytest
from model_bakery import baker

from nsc.utils import models as utils


# All tests require the database
pytestmark = pytest.mark.django_db


def test_get_apps():
    actual = [app.name for app in utils.get_apps()]
    assert "django.contrib.auth" in actual


def test_get_project_apps():
    apps = {app.name.split(".")[0] for app in utils.get_project_apps("django.")}
    assert {"django"} == apps


def test_get_model():
    klass = utils.get_model("auth.User")
    assert klass._meta.object_name == "User"
    assert klass._meta.app_label == "auth"


def test_get_models():
    names = [klass._meta.object_name for klass in utils.get_models()]
    assert "LogEntry" in names
    assert "Policy" in names


def test_get_fields():
    names = [field.name for field in utils.get_fields()]
    assert "first_name" in names
    assert "is_active" in names


def test_get_field():
    field = utils.get_field("auth.User", "first_name")
    assert isinstance(field, models.CharField)


def test_get_app_models():
    app = utils.get_project_apps("django.contrib.auth")[0]
    names = [klass._meta.object_name for klass in utils.get_app_models(app)]
    assert "User" in names


def test_get_model_fields():
    names = [
        field.name for field in utils.get_model_fields(utils.get_model("auth.User"))
    ]
    assert "first_name" in names
    assert "last_name" in names
    assert "email" in names


def test_is_pk():
    field = utils.get_field("auth.User", "id")
    assert utils.is_pk(field)
    field = utils.get_field("auth.User", "first_name")
    assert not utils.is_pk(field)


def test_is_fk():
    field = utils.get_field("auth.Permission", "content_type")
    assert utils.is_fk(field)
    field = utils.get_field("auth.Permission", "name")
    assert not utils.is_fk(field)


def test_is_reverse_fk():
    field = utils.get_field("contenttypes.ContentType", "permission")
    assert utils.is_reverse_fk(field)
    field = utils.get_field("contenttypes.ContentType", "app_label")
    assert not utils.is_reverse_fk(field)


def test_is_one_to_one():
    field = utils.get_field("policy.Policy", "condition")
    assert utils.is_one_to_one(field)
    field = utils.get_field("policy.Policy", "name")
    assert not utils.is_one_to_one(field)


def test_is_text_field():
    field = utils.get_field("auth.User", "first_name")
    assert utils.is_text_field(field)
    field = utils.get_field("auth.User", "is_staff")
    assert not utils.is_text_field(field)


def test_is_allowed():
    field = utils.get_field("auth.User", "email")
    assert utils.is_allowed(field, "user@example.com")
    assert not utils.is_allowed(field, "user+example.com")


def test_is_fetched():
    instance = baker.make(get_user_model())
    assert hasattr(instance, "_state")
    assert hasattr(getattr(instance, "_state"), "fields_cache")


def test_all_subclasses():
    from django.db.models import Model

    names = [klass._meta.object_name for klass in utils.all_subclasses(Model)]
    assert "User" in names
    assert "Group" in names
