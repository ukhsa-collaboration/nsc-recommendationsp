from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from model_bakery import baker

from nsc.condition.models import Condition
from nsc.policy.models import Policy
from nsc.utils.admin import get_change_url, get_change_models


class AdminChangeViewTests(TestCase):
    """
    Tests to verify the admin change view is displayed without error.

    Todo:
        * Add more factory instances so all the change views are covered.
          See the commented out section with the 'remaining' list.
        * The user can probably be removed from the factories used to create
          the instances since any user will do. Note however some factories
          force the user to be set explicitly so test data is setup correctly.

    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

    def get_view(self, instance):
        return self.client.get(get_change_url(instance), follow=False)

    def setUp(self):
        self.client.force_login(self.user)

    def tearDown(self):
        self.client.logout()

    def test_change_views(self):
        instances = {
            'Condition': baker.make(Condition),
            'Policy': baker.make(Policy),
        }

        # remaining = [model for model in self.models
        #              if admin.site._registry[model].has_change_permission(self.request) and
        #              model.__name__ not in instances]
        #
        # print(remaining)

        models = [model for model in get_change_models(admin.site, self.user)
                  if model.__name__ in instances]

        for model in models:
            with self.subTest(model=model):
                instance = instances[model.__name__]
                self.assertEqual(self.get_view(instance).status_code, 200)
