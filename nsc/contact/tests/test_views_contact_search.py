"""
This file tests the search functionality in the Contact admin page.
It verifies that users can search contacts by:
- Contact name
- Phone number
- Stakeholder name
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import pytest

from nsc.stakeholder.models import Stakeholder

from ..models import Contact


@pytest.mark.django_db
class TestContactSearch(TestCase):
    """
    Tests for the contact search feature in Django admin.
    We create two test contacts and verify we can search for them.
    """

    def setUp(self):
        """
        Set up our test data. We create:
        1. An admin user who can access the admin page
        2. A company (stakeholder) called "Test Company"
        3. Two contacts: "John Smith" and "Jane Doe"
        """
        # 1. Create an admin user who can log in to admin
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="testadmin",
            email="testadmin@example.com",
            password="password123",
        )
        # Log in as the admin user
        self.client.login(username="testadmin", password="password123")

        # 2. Create a company
        self.company = Stakeholder.objects.create(name="Test Company")

        # 3. Create two contacts that work at the company
        self.john = Contact.objects.create(
            name="John Smith", phone="12345", stakeholder=self.company
        )

        self.jane = Contact.objects.create(
            name="Jane Doe", phone="67890", stakeholder=self.company
        )

        # Get the URL of the admin page where we can search contacts
        self.search_url = reverse("admin:contact_contact_changelist")

    def test_search_by_contact_name(self):
        """
        Test that we can find contacts by searching their names.
        Example: Searching for "John" should find "John Smith" but not "Jane Doe"
        """
        # Search for "John" - should find John Smith
        response = self.client.get(f"{self.search_url}?q=John")
        self.assertContains(response, "12345")  # John's phone
        self.assertContains(response, "1 contact")  # Should only find one contact

        # Search for "Jane" - should find Jane Doe
        response = self.client.get(f"{self.search_url}?q=Jane")
        self.assertContains(response, "67890")  # Jane's phone
        self.assertContains(response, "1 contact")  # Should only find one contact

    def test_search_by_phone_number(self):
        """
        Test that we can find contacts by searching their phone numbers.
        Example: Searching for "12345" should find "John Smith"
        """
        # Search using John's phone
        response = self.client.get(f"{self.search_url}?q=12345")
        self.assertContains(response, "John Smith")
        self.assertContains(response, "1 contact")

        # Search using Jane's phone
        response = self.client.get(f"{self.search_url}?q=67890")
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "1 contact")

    def test_search_by_company_name(self):
        """
        Test that we can find contacts by searching their company name.
        Example: Searching for "Test Company" should find both contacts
        """
        # Search by company name - should find both contacts
        response = self.client.get(f"{self.search_url}?q=Test Company")
        self.assertContains(response, "John Smith")  # Should find John
        self.assertContains(response, "Jane Doe")  # Should find Jane
        self.assertContains(response, "2 contacts")  # Should find both contacts

    def test_no_search_results(self):
        """
        Test that searching for something that doesn't exist returns no results.
        Example: Searching for "XYZ" should find no contacts
        """
        response = self.client.get(f"{self.search_url}?q=XYZ")
        self.assertContains(response, "0 contacts")
