from django.contrib.admin import site
from django.contrib.auth.models import User
from django.test import TestCase

from model_bakery import baker

from nsc.utils import admin as utils


class AdminUtilTests(TestCase):
    """
    The admin utils module, nsc.utils.admin, is a collection of utility
    functions that is used to get the Django Admin view so they can be
    smoke tested - essentially is the page displayed with no errors.

    """
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(User, is_superuser=True)

    def test_get_add_url(self):
        self.assertEqual('/admin/auth/user/add/', utils.get_add_url(User))

    def test_get_change_url(self):
        expected = '/admin/auth/user/%s/change/' % self.user.pk
        self.assertEqual(expected, utils.get_change_url(self.user))

    def test_get_delete_url(self):
        expected = '/admin/auth/user/%s/delete/' % self.user.pk
        self.assertEqual(expected, utils.get_delete_url(self.user))

    def test_get_changelist_url(self):
        self.assertEqual('/admin/auth/user/', utils.get_changelist_url(User))

    def test_get_models(self):
        names = [model._meta.object_name for model in utils.get_models(site)]
        self.assertIn('User', names)
        self.assertIn('Group', names)

    def test_get_add_models(self):
        names = [model._meta.object_name for model in utils.get_add_models(site, self.user)]
        self.assertIn('User', names)
        self.assertIn('Group', names)

    def test_get_change_models(self):
        names = [model._meta.object_name for model in utils.get_change_models(site, self.user)]
        self.assertIn('User', names)
        self.assertIn('Group', names)

    def test_get_delete_models(self):
        names = [model._meta.object_name for model in utils.get_change_models(site, self.user)]
        self.assertIn('User', names)
        self.assertIn('Group', names)
