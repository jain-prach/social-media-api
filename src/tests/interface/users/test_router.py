import uuid

from sqlmodel import select

from src.domain.models import BaseUser
from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import before_create_base_user_admin, before_create_base_user, before_admin_login_cred, before_user_login_cred
from src.tests.test_utils import create_session, get_auth_header
from src.tests.test_data import create_admin, create_user

def test_list_base_users(before_admin_login_cred, before_create_base_user):
    session = create_session()
    token = before_admin_login_cred(session)
    before_create_base_user(session=session, user_dict=create_user())
    response = client.get("/base-users/", headers=get_auth_header(token))
    data = response.json()["data"]
    session.close()
    assert response.status_code == 200
    assert len(data) == 2

def test_list_base_users_with_user_login(before_user_login_cred, before_create_base_user_admin, before_create_base_user):
    session = create_session()
    token = before_user_login_cred(session)
    before_create_base_user_admin(session=session, user_dict=create_admin())
    before_create_base_user(session=session, user_dict=create_user())
    response = client.get("/base-users/", headers=get_auth_header(token))
    data = response.json()["data"]
    session.close()
    assert response.status_code == 200
    assert len(data) == 1

def test_get_base_user(before_admin_login_cred, before_create_base_user):
    session = create_session()
    token=before_admin_login_cred(session)
    user=before_create_base_user(session=session, user_dict=create_user())
    session.close()
    response = client.get(f"/base-user/{user.id}/", headers=get_auth_header(token))
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["id"] == str(user.id)


def test_get_base_user_for_no_data(before_admin_login_cred, before_create_base_user):
    session = create_session()
    token=before_admin_login_cred(session)
    session.close()
    response = client.get(f"/base-user/{uuid.uuid4()}/", headers=get_auth_header(token))
    assert response.status_code == 404

def test_get_base_user_with_user_login(before_user_login_cred, before_create_base_user):
    session = create_session()
    token=before_user_login_cred(session=session)
    user=before_create_base_user(session=session, user_dict=create_user())
    session.close()
    response = client.get(f"/base-user/{user.id}/", headers=get_auth_header(token))
    assert response.status_code == 403

def test_get_own_details(before_user_login_cred):
    session=create_session()
    token=before_user_login_cred(session=session)
    session.close()
    response = client.get("/base-user/get/me/", headers=get_auth_header(token))
    assert response.status_code == 200

def test_delete_base_user(before_admin_login_cred, before_create_base_user):
    session=create_session()
    token=before_admin_login_cred(session=session)
    user=before_create_base_user(session=session, user_dict=create_user())
    response = client.delete(f"/base-user/{user.id}/", headers=get_auth_header(token))
    users = session.exec(select(BaseUser)).all()
    session.close()
    assert response.status_code == 200
    assert user not in users

def test_delete_base_user_with_user_login(before_user_login_cred, before_create_base_user):
    session=create_session()
    token=before_user_login_cred(session=session)
    user=before_create_base_user(session=session, user_dict=create_user())
    response = client.delete(f"/base-user/{user.id}/", headers=get_auth_header(token))
    users = session.exec(select(BaseUser)).all()
    session.close()
    assert response.status_code == 403
    assert user in users