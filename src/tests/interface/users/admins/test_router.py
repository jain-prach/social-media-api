<<<<<<< HEAD
from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import before_create_private_user_login_cred

# def test_get_reported_posts(before_create_private_user_login_cred)
=======
import uuid

from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_create_private_user_login_cred,
    before_admin_login_cred,
    before_create_base_user,
    before_create_normal_user,
    before_create_post,
    before_report_post,
)
from src.tests.test_utils import create_session, get_auth_header
from src.tests.test_data import create_private_user, create_public_user


def test_get_reported_posts(before_admin_login_cred):
    session = create_session()
    token = before_admin_login_cred(session=session)
    response = client.get(
        "/admin/reported_posts/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 0
    session.close()


def test_get_reported_posts_when_post_reported(
    before_admin_login_cred, before_report_post
):
    session = create_session()
    token = before_admin_login_cred(session=session)
    before_report_post(
        session=session,
        posted_by=create_public_user(),
        reported_by=create_private_user(),
    )
    response = client.get(
        "/admin/reported_posts/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    session.close()


def test_get_reported_posts_with_unauthorized_access():
    response = client.get("/admin/reported_posts/")
    assert response.status_code == 401


def test_get_reported_posts_by_user_login(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.get(
        "/admin/reported_posts/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 403


def test_delete_reported_post(before_admin_login_cred, before_report_post):
    session = create_session()
    token = before_admin_login_cred(session=session)
    reported = before_report_post(
        session=session, posted_by=create_public_user(), reported_by=create_private_user()
    )
    response = client.delete(
        f"/admin/reported_posts/{reported.post.id}/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 200


def test_delete_post_not_reported(before_admin_login_cred, before_create_post):
    session = create_session()
    token = before_admin_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_private_user())
    response = client.delete(
        f"/admin/reported_posts/{post.id}/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 400

def test_delete_reported_post_for_no_post_found(before_admin_login_cred):
    session = create_session()
    token = before_admin_login_cred(session=session)
    response = client.delete(
        f"/admin/reported_posts/{uuid.uuid4()}/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 404

def test_delete_reported_post_with_unauthorized_access():
    response = client.delete(f"/admin/reported_posts/{uuid.uuid4()}/")
    assert response.status_code == 401


def test_delete_reported_post_by_user_login(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.delete(
        f"/admin/reported_posts/{uuid.uuid4()}/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 403
>>>>>>> db81b47e93c4576a973deb70e666e05a70868fe3
