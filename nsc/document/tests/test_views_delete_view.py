from django.urls import reverse

import pytest

# All tests require the database
from nsc.document.models import Document


pytestmark = pytest.mark.django_db


@pytest.fixture
def url(review_document):
    return reverse("document:delete", kwargs={"pk": review_document.pk})


@pytest.fixture
def response(url, django_app_factory, erm_user):
    return django_app_factory(csrf_checks=False).post(url, user=erm_user)


def test_delete(response):
    assert response.status == "302 Found"
    assert Document.objects.count() == 0


def test_delete__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_delete__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)
