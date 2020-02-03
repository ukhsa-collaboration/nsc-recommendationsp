from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from nsc.utils.admin import get_changelist_url, get_models


class AdminChangelistViewTests(TestCase):
    """
    Tests to verify the admin changelist views are displayed without error.

    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser("admin", "admin@example.com", "admin")

    def get_view(self, model):
        url = get_changelist_url(model)
        return self.client.get(url, follow=False)

    def setUp(self):
        self.client.force_login(self.user)

    def tearDown(self):
        self.client.logout()

    def test_changelist_views(self):
        for model in get_models(admin.site):
            with self.subTest(model=model):
                self.assertEqual(self.get_view(model).status_code, 200)
