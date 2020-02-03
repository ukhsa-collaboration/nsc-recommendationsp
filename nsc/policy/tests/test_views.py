from django.urls import reverse

from django_webtest import WebTest
from model_bakery import baker

from ..models import Policy


class PolicyListTests(WebTest):

    url = reverse("policy:list")

    def search(self, **kwargs):
        form = self.app.get(self.url).form
        for field, value in kwargs.items():
            form[field] = value
        return form.submit()

    def test_list_view(self):
        """
        Test that the list view returns the list of policies.
        """
        instance = baker.make(Policy)
        response = self.app.get(self.url)
        self.assertIn(instance, response.context["object_list"])
        self.assertFalse(response.context["is_paginated"])
        self.assertEqual(response.context["paginator"].num_pages, 1)

    def test_list_view_query_count(self):
        """
        Test that fetching the list takes a fixed number of queries.
        """
        baker.make(Policy, _quantity=1)
        self.assertNumQueries(2, self.app.get, self.url)
        baker.make(Policy, _quantity=9)
        self.assertNumQueries(2, self.app.get, self.url)

    def test_list_view_is_paginated(self):
        """
        Test pagination is not shown for small numbers of policies.
        """
        baker.make(Policy, _quantity=50)
        response = self.app.get(self.url)
        self.assertTrue(response.context["is_paginated"])
        self.assertGreater(response.context["paginator"].num_pages, 1)

    def test_search_form_blank(self):
        """
        Test that the fields in the search form are initially blank.
        """
        form = self.app.get(self.url).form
        self.assertEqual(form["condition"].value, "")
        self.assertEqual(form["affects"].value, None)
        self.assertEqual(form["screen"].value, None)

    def test_search_on_condition_name(self):
        """
        Test the list of policies can be filtered by the condition name.
        """
        baker.make(Policy, name="condition")
        response = self.search(condition="other")
        self.assertFalse(response.context["object_list"])

    def test_search_on_age_affected(self):
        """
        Test the list of policies can be filtered by the age of those affected.
        """
        baker.make(Policy, condition__ages="{adult}")
        response = self.search(affects="child")
        self.assertFalse(response.context["object_list"])

    def test_search_on_recommendation(self):
        """
        Test the list of policies can be filtered by whether the condition is
        screened for or not.
        """
        baker.make(Policy, is_screened=False)
        response = self.search(screen="yes")
        self.assertFalse(response.context["object_list"])

    def test_search_form_shows_condition_term(self):
        """
        Test when the search results are shown the form shows the entered condition name.
        """
        form = self.search(condition="name").form
        self.assertEqual(form["condition"].value, "name")
        self.assertEqual(form["affects"].value, None)
        self.assertEqual(form["screen"].value, None)

    def test_search_form_shows_affects_term(self):
        """
        Test when the search results are shown the form shows the selected age.
        """
        form = self.search(affects="child").form
        self.assertEqual(form["condition"].value, "")
        self.assertEqual(form["affects"].value, "child")
        self.assertEqual(form["screen"].value, None)

    def test_search_form_shows_screen_term(self):
        """
        Test when the search results are shown the form shows the selected recommendation.
        """
        form = self.search(screen="no").form
        self.assertEqual(form["condition"].value, "")
        self.assertEqual(form["affects"].value, None)
        self.assertEqual(form["screen"].value, "no")


class PolicyDetailTests(WebTest):
    def test_detail_view(self):
        """
        Test that we can view an instance via the detail view.
        """
        instance = baker.make(Policy)
        response = self.app.get(instance.get_absolute_url())
        self.assertEqual(response.context['object'], instance)

    def test_back_link(self):
        """
        Test the back link returns to the previous page. This ensures that
        search results are not lost.
        """
        instance = baker.make(Policy, name='condition', condition__ages='{child}')
        form = self.app.get(reverse('policy:list')).form
        form['affects'] = 'child'
        results = form.submit()
        detail = results.click(href=instance.get_absolute_url())
        referer = detail.click(linkid='referer-link-id')
        self.assertEqual(results.request.url, referer.request.url)
