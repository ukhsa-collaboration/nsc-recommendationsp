from django.urls import reverse

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url(make_review, django_app):
    review = make_review()
    url = reverse("review:delete", kwargs={"slug": review.slug})
    return url


@pytest.fixture
def response(url, erm_user, django_app):
    return django_app.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_view(response):
    """
    Test that the page can be displayed.
    """
    assert response.status_code == 200


def test_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_view__not_user(url, test_access_not_user_can_access):
    test_access_not_user_can_access(url=url)


def test_back_link(response, dom):
    """
    Test the back link returns to the review detail page.
    """
    review = response.context["object"]
    link = dom.find(id="back-link-id")
    assert link["href"] == review.get_absolute_url()

import pytest
from django.urls import reverse

def test_logout_functionality(client, django_user_model, settings):
    # Force the setting to False for the test
    settings.AUTH_USE_ACTIVE_DIRECTORY = False

    # Create a user and log them in
    username = "user"
    password = "pass"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)

    # Ensure user is authenticated
    response = client.get(reverse("login"))
    assert response.wsgi_request.user.is_authenticated

    # Perform logout
    response = client.post(reverse("logout"), follow=True)

    # After logout, user should be anonymous
    assert not response.wsgi_request.user.is_authenticated

    # Should be redirected to login page
    assert response.status_code == 200
    assert b"Login" in response.content 
