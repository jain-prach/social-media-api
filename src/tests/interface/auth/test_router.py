import pytest

from tests.test_client import client, setup_database
from tests.test_dicts import created_user_login, created_admin_login, admin_registration


@pytest.fixture(scope="function")
def get_staff_access_login_token():
    """generate login access token for staff login"""
    response = client.post(
        url="/auth/login/", json=created_admin_login
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def get_user_access_login_token():
    """generate login access token for user login"""
    response = client.post(
        url="/auth/login/", json=created_user_login
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_staff_user():
    """create staff user"""
    response = client.post(
        url="/users/create/",
        json=admin_registration,
    )
    print(response.json()['data'])
    assert response.status_code == 201