from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_user_login_cred,
    before_admin_login_cred,
    before_create_base_user,
    before_create_base_user_admin,
    before_create_normal_user,
    before_create_public_user_login_cred, 
    before_create_private_user_login_cred
)
from src.tests.test_data import create_user, create_public_user, create_private_user, get_username
from src.tests.test_utils import create_session, get_auth_header


def test_list_users(before_admin_login_cred, before_create_normal_user):
    session = create_session()
    token = before_admin_login_cred(session)
    before_create_normal_user(session=session, user_dict=create_public_user())
    before_create_normal_user(session=session, user_dict=create_private_user())
    session.close()
    response = client.get("/users/", headers=get_auth_header(token))
    data = response.json()["data"]
    print(data)
    assert response.status_code == 200
    assert len(data) == 2
    
def test_list_users_with_user_login(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    session.close()
    response = client.get("/users/", headers=get_auth_header(token))
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 1
    
def test_get_user(before_create_private_user_login_cred, before_create_normal_user):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    session.close()
    response = client.get(f"user/{user1.username}/", headers=get_auth_header(token))
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["username"] == user1.username
    
def test_get_user_for_user_not_found(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    session.close()
    response = client.get(f"user/{get_username()}/", headers=get_auth_header(token))
    data = response.json()["data"]
    assert response.status_code == 404
    
def test_update_user(before_create_public_user_login_cred):
    session=create_session()
    token=before_create_public_user_login_cred(session=session)
    session.close()
    response = client.put("user/", headers=get_auth_header(token))
    #multipart form data