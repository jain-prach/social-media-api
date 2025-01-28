from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_user_login_cred,
    before_admin_login_cred,
    before_create_base_user,
    before_create_base_user_admin,
    before_create_normal_user,
    before_create_public_user_login_cred,
    before_create_private_user_login_cred,
)
from src.tests.test_data import (
    create_user,
    create_public_user,
    create_private_user,
    get_username,
)
from src.tests.test_utils import create_session, get_auth_header
from lib.fastapi.custom_enums import ProfileType
from src.application.users.services import JWTService


def test_list_users(before_admin_login_cred, before_create_normal_user):
    session = create_session()
    token = before_admin_login_cred(session)
    before_create_normal_user(session=session, user_dict=create_public_user())
    before_create_normal_user(session=session, user_dict=create_private_user())
    session.close()
    response = client.get("/users/", headers=get_auth_header(token))
    data = response.json()["data"]
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
    assert response.status_code == 404


def test_update_user(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    session.close()
    update_dict = {"username": get_username(), "bio": "New bio", "profile_type": ProfileType.PRIVATE.value}
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.put(
            "user/",
            headers=get_auth_header(token),
            data=update_dict,
            files={"profile": (" spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", f)},
        )
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["username"] == update_dict["username"]

def test_delete_user(before_create_public_user_login_cred):
    session=create_session()
    token=before_create_public_user_login_cred(session=session)
    session.close()
    payload = JWTService().decode(token)
    response = client.delete(f"user/{payload["id"]}", headers=get_auth_header(token))
    assert response.status_code == 200

def test_delete_user_with_admin(before_admin_login_cred, before_create_normal_user):
    session=create_session()
    token=before_admin_login_cred(session=session)
    user=before_create_normal_user(session=session, user_dict=create_private_user())
    session.close()
    response = client.delete(f"user/{user.base_user_id}", headers=get_auth_header(token))
    assert response.status_code == 200