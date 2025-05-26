from django.urls import reverse

import pytest

from nsc.notify.models import Email, ReceiptUserToken


# All tests require the database
pytestmark = pytest.mark.django_db


def test_request_is_get_response_is_not_allowed(client):
    assert client.get(reverse("notify:receipt"), expect_errors=True).status_code == 405


def test_no_auth_set_response_is_forbidden(client):
    assert client.post(reverse("notify:receipt"), expect_errors=True).status_code == 403


@pytest.mark.parametrize(
    "token", ["bearer123", "token 123", "bearer", "bearer 123 456"]
)
def test_auth_header_is_badly_formed_set_response_is_forbidden(token, client):
    assert (
        client.post(
            reverse("notify:receipt"),
            expect_errors=True,
            headers={"Authorization": token},
        ).status_code
        == 403
    )


def test_token_does_not_match_a_token_response_is_forbidden(client):
    token = ReceiptUserToken.objects.first()

    assert (
        client.post(
            reverse("notify:receipt"),
            expect_errors=True,
            headers={"Authorization": f"bearer {token.token}-extra"},
        ).status_code
        == 403
    )


@pytest.mark.parametrize(
    "new_status",
    [
        Email.STATUS.delivered,
        Email.STATUS.permanent_failure,
        Email.STATUS.temporary_failure,
        Email.STATUS.technical_failure,
    ],
)
def test_email_object_doesnt_exist_is_not_found(new_status, client, make_email):
    token = ReceiptUserToken.objects.first()
    email = make_email(status=Email.STATUS.sending)

    assert (
        client.post(
            reverse("notify:receipt"),
            expect_errors=True,
            headers={"Authorization": f"bearer {token.token}"},
            data={"reference": email.id + 1, "status": new_status},
        ).status_code
        == 404
    )


@pytest.mark.parametrize(
    "new_status",
    [
        Email.STATUS.delivered,
        Email.STATUS.permanent_failure,
        Email.STATUS.temporary_failure,
        Email.STATUS.technical_failure,
    ],
)
def test_status_is_not_valid_response_is_bad_data(new_status, client, make_email):
    token = ReceiptUserToken.objects.first()
    email = make_email(status=Email.STATUS.sending)

    assert (
        client.post(
            reverse("notify:receipt"),
            expect_errors=True,
            headers={"Authorization": f"bearer {token.token}"},
            data={"reference": email.id, "status": f"{new_status}-extra"},
        ).status_code
        == 400
    )


@pytest.mark.parametrize(
    "new_status",
    [
        Email.STATUS.delivered,
        Email.STATUS.permanent_failure,
        Email.STATUS.temporary_failure,
        Email.STATUS.technical_failure,
    ],
)
def test_status_is_valid_email_is_updated(new_status, client, make_email):
    token = ReceiptUserToken.objects.first()
    email = make_email(status=Email.STATUS.sending)

    client.post(
        reverse("notify:receipt"),
        expect_errors=True,
        headers={"Authorization": f"bearer {token.token}"},
        data={"reference": email.id, "status": new_status},
    )

    updated_email = Email.objects.get(id=email.id)

    assert updated_email.status == new_status
