from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_user_login_cred,
    before_admin_login_cred,
    before_create_base_user,
    before_create_base_user_admin,
    before_create_public_user,
    before_create_private_user,
)
from src.tests.test_data import create_user
from src.tests.test_utils import create_session, get_auth_header


def test_list_users(before_admin_login_cred, before_create_public_user, before_create_private_user):
    session = create_session()
    token = before_admin_login_cred(session)
    before_create_public_user(session=session)
    before_create_private_user(session=session)
    session.close()
    response = client.get("/users/", headers=get_auth_header(token))
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 2
