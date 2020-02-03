from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase

from model_bakery import baker

from nsc.utils import models as utils


class ModelUtilTests(TestCase):
    """
    The model utils module, nsc.utils.models, is a collection of utility
    functions that process the metadata of Django apps and models. Since
    this sometimes changes with new releases the tests here are used to
    identify any problems more easily than debugging the tests that use
    the functions.

    """

    def test_get_apps(self):
        actual = [app.name for app in utils.get_apps()]
        self.assertIn("django.contrib.auth", actual)

    def test_get_project_apps(self):
        apps = {app.name.split(".")[0] for app in utils.get_project_apps("django.")}
        self.assertSetEqual({"django"}, apps)

    def test_get_model(self):
        klass = utils.get_model("auth.User")
        self.assertEqual(klass._meta.object_name, "User")
        self.assertEqual(klass._meta.app_label, "auth")

    def test_get_models(self):
        names = [klass._meta.object_name for klass in utils.get_models()]
        self.assertIn("LogEntry", names)
        self.assertIn("Policy", names)

    def test_get_fields(self):
        names = [field.name for field in utils.get_fields()]
        self.assertIn("first_name", names)
        self.assertIn("is_active", names)

    def test_get_field(self):
        field = utils.get_field("auth.User", "first_name")
        self.assertIsInstance(field, models.CharField)

    def test_get_app_models(self):
        app = utils.get_project_apps("django.contrib.auth")[0]
        names = [klass._meta.object_name for klass in utils.get_app_models(app)]
        self.assertIn("User", names)

    def test_get_model_fields(self):
        names = [
            field.name for field in utils.get_model_fields(utils.get_model("auth.User"))
        ]
        self.assertIn("first_name", names)
        self.assertIn("last_name", names)
        self.assertIn("email", names)

    def test_is_pk(self):
        field = utils.get_field("auth.User", "id")
        self.assertTrue(utils.is_pk(field))
        field = utils.get_field("auth.User", "first_name")
        self.assertFalse(utils.is_pk(field))

    def test_is_fk(self):
        field = utils.get_field("auth.Permission", "content_type")
        self.assertTrue(utils.is_fk(field))
        field = utils.get_field("auth.Permission", "name")
        self.assertFalse(utils.is_fk(field))

    def test_is_reverse_fk(self):
        field = utils.get_field("contenttypes.ContentType", "permission")
        self.assertTrue(utils.is_reverse_fk(field))
        field = utils.get_field("contenttypes.ContentType", "app_label")
        self.assertFalse(utils.is_reverse_fk(field))

    def test_is_one_to_one(self):
        field = utils.get_field("policy.Policy", "condition")
        self.assertTrue(utils.is_one_to_one(field))
        field = utils.get_field("policy.Policy", "name")
        self.assertFalse(utils.is_one_to_one(field))

    def test_is_text_field(self):
        field = utils.get_field("auth.User", "first_name")
        self.assertTrue(utils.is_text_field(field))
        field = utils.get_field("auth.User", "is_staff")
        self.assertFalse(utils.is_text_field(field))

    def test_is_allowed(self):
        field = utils.get_field("auth.User", "email")
        self.assertTrue(utils.is_allowed(field, "user@example.com"))
        self.assertFalse(utils.is_allowed(field, "user+example.com"))

    def test_is_fetched(self):
        instance = baker.make(User)
        self.assertTrue(hasattr(instance, "_state"))
        self.assertTrue(hasattr(getattr(instance, "_state"), "fields_cache"))

    def test_all_subclasses(self):
        from django.db.models import Model

        names = [klass._meta.object_name for klass in utils.all_subclasses(Model)]
        self.assertIn("User", names)
        self.assertIn("Group", names)
