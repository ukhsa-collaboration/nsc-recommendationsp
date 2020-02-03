from django_webtest import WebTest
from model_bakery import baker

from nsc.utils.models import is_fetched

from ..models import Policy


class PolicyModelTest(WebTest):
    def test_factory_create(self):
        """
        Test that we can create an instance via our object factory.
        """
        instance = baker.make(Policy)
        self.assertTrue(isinstance(instance, Policy))

    def test_active(self):
        """
        Test the active() method on the manager only returns active policies.
        """
        baker.make(Policy, is_active=True)
        baker.make(Policy, is_active=False)
        expected = [obj.pk for obj in Policy.objects.filter(is_active=True)]
        actual = [obj.pk for obj in Policy.objects.active()]
        self.assertListEqual(expected, actual)

    def test_active_selected_related(self):
        """
        Test that Policy object fetches also include Conditions.
        """
        baker.make(Policy, is_active=True)
        policy = Policy.objects.active().first()
        self.assertTrue(is_fetched(policy, "condition"))
