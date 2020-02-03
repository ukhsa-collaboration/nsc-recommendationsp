from django_webtest import WebTest
from model_bakery import baker

from nsc.condition.models import Condition


class ConditionTest(WebTest):
    def test_factory_create(self):
        """
        Test that we can create an instance via our object factory.
        """
        instance = baker.make(Condition)
        self.assertTrue(isinstance(instance, Condition))
