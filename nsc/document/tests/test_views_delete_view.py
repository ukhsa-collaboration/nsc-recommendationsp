from django.test import Client
from django.urls import reverse

import pytest

# All tests require the database
from nsc.document.models import Document


pytestmark = pytest.mark.django_db


@pytest.fixture
def url(review_document):
    return reverse("document:delete", kwargs={"pk": review_document.pk})


@pytest.fixture
def client_factory():
    def factory(csrf_checks=True):
        return Client(enforce_csrf_checks=csrf_checks)

    return factory


@pytest.fixture
def response(url, client_factory, erm_user):
    client = client_factory(csrf_checks=False)
    client.force_login(erm_user)
    return client.post(url)


def test_delete(response):
    assert response.status_code == 302
    assert Document.objects.count() == 0


def test_delete__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_delete__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)
