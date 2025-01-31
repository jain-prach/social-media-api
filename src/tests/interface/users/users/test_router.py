import uuid

from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_user_login_cred,
    before_admin_login_cred,
    before_create_base_user,
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
from src.tests.test_utils import create_session, get_auth_header, get_user_by_token
from lib.fastapi.custom_enums import ProfileType
from src.application.users.services import JWTService
from src.domain.models import User


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


def test_list_users_with_unauthorized_access():
    response = client.get(
        "/users/",
    )
    assert response.status_code == 401


def test_get_user(before_create_private_user_login_cred, before_create_normal_user):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    response = client.get(f"/user/{user1.username}/", headers=get_auth_header(token))
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["username"] == user1.username
    session.close()


def test_get_user_for_user_not_found(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    response = client.get(f"user/{get_username()}/", headers=get_auth_header(token))
    assert response.status_code == 404
    session.close()


def test_get_user_with_unauthorized_access():
    response = client.get(f"/user/{get_username()}/")
    assert response.status_code == 401

def test_get_user_with_admin_login(before_admin_login_cred, before_create_normal_user):
    session = create_session()
    token = before_admin_login_cred(session=session)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    response = client.get(f"/user/{user1.username}/", headers=get_auth_header(token))
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["username"] == user1.username
    session.close()

def test_update_user(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    update_dict = {
        "username": get_username(),
        "bio": "New bio",
        "profile_type": ProfileType.PRIVATE.value,
    }
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.put(
            "/user/",
            headers=get_auth_header(token),
            data=update_dict,
            files={"profile": ("spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", f)},
        )
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["username"] == update_dict["username"]
    session.close()

def test_update_user_with_unauthorized_access():
    response = client.put("/user/")
    assert response.status_code == 401

def test_update_user_with_invalid_username(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    update_dict = {
        "username": " invalid@ ",
        "bio": "New bio",
        "profile_type": ProfileType.PRIVATE.value,
    }
    response = client.put(
        "/user/",
        headers=get_auth_header(token),
        data=update_dict,
    )
    assert response.status_code == 422
    session.close()

def test_update_user_with_invalid_username_max_length(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    update_dict = {
        "username": "Loremipsumdolorsitametconsecteturadipiscingelit",
        "bio": "New bio",
        "profile_type": ProfileType.PRIVATE.value,
    }
    response = client.put(
        "/user/",
        headers=get_auth_header(token),
        data=update_dict,
    )
    assert response.status_code == 422
    session.close()

def test_update_user_with_whitespaces_in_bio(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    update_dict = {
        "username": get_username(),
        "bio": "       New bio                ",
        "profile_type": ProfileType.PRIVATE.value,
    }
    response = client.put(
        "/user/",
        headers=get_auth_header(token),
        data=update_dict,
    )
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["username"] == update_dict.get("username")
    assert data["bio"] == update_dict.get("bio").strip()
    session.close()

def test_delete_user(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    payload = JWTService().decode(token)
    response = client.delete(f"/user/{payload.get('id')}", headers=get_auth_header(token))
    assert response.status_code == 200
    db_user = get_user_by_token(session=session, token=token)
    assert db_user is None
    session.close()

def test_delete_user_with_unauthorized_access():
    response = client.delete(f"/user/{uuid.uuid4()}")
    assert response.status_code == 401

def test_delete_user_with_admin(before_admin_login_cred, before_create_normal_user):
    session = create_session()
    token = before_admin_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    response = client.delete(
        f"/user/{user.base_user_id}/", headers=get_auth_header(token)
    )
    user_id = user.id
    session.close()
    session = create_session()
    assert response.status_code == 200
    db_user = session.get(User, user_id)
    assert db_user is None
    session.close()

def test_delete_another_user(before_create_public_user_login_cred, before_create_normal_user):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    response = client.delete(f"/user/{user.id}/", headers=get_auth_header(token))
    assert response.status_code == 403
    db_user = session.get(User, user.id)
    assert db_user is not None
    session.close()