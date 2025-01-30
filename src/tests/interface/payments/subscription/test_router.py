from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_create_private_user_login_cred,
    before_create_base_user,
    before_create_normal_user,
    before_admin_login_cred,
)
from src.tests.test_utils import create_session, get_auth_header
from lib.fastapi.custom_enums import SubscriptionInterval


def test_subscribe(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.get(
        "/payment/subscribe/",
        params={"subscription": SubscriptionInterval.DAILY.value},
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 200
    assert response.json()["data"]["url"] != "" or None


def test_subscribe_invalid_subscription_value(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.get(
        "/payment/subscribe/",
        params={"subscription": "invalid"},
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 422


def test_subscribe_no_subscription_value(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.get(
        "/payment/subscribe/",
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 422


def test_subscribe_with_unauthorized_access():
    response = client.get("/payment/subscribe/")
    assert response.status_code == 401


def test_subscribe_with_admin_login(before_admin_login_cred):
    session = create_session()
    token = before_admin_login_cred(session=session)
    response = client.get(
        "/payment/subscribe/",
        params={"subscription": SubscriptionInterval.DAILY.value},
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 403
