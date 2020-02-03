from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from nsc.utils.admin import get_add_models, get_add_url


class AdminAddViewTests(TestCase):
    """
    Tests to verify the admin add views are displayed without error.

    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser("admin", "admin@example.com", "admin")

    def get_view(self, model):
        return self.client.get(get_add_url(model), follow=False)

    def setUp(self):
        self.client.force_login(self.user)

    def tearDown(self):
        self.client.logout()

    def test_add_views(self):
        for model in get_add_models(admin.site, self.user):
            with self.subTest(model=model):
                self.assertEqual(self.get_view(model).status_code, 200)
