import uuid

from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_create_post,
    before_create_normal_user,
    before_create_base_user,
    before_create_private_user_login_cred,
    before_admin_login_cred,
    before_create_approved_follow_requests,
)
from src.tests.test_utils import create_session, get_auth_header, get_user_by_token
from src.tests.test_data import create_private_user, create_public_user


def test_comment_post(before_create_private_user_login_cred, before_create_post):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_public_user())
    response = client.post(
        f"/comment/{post.id}",
        headers=get_auth_header(token=token),
        json={"comment": "commenting on post"},
    )
    assert response.status_code == 200
    session.refresh(post)
    assert len(post.comments) == 1
    session.close()


def test_comment_post_with_unauthorized_access():
    response = client.post(f"/comment/{uuid.uuid4()}")
    assert response.status_code == 401


def test_comment_post_for_no_post_created(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.post(
        f"/comment/{uuid.uuid4()}",
        headers=get_auth_header(token=token),
        json={"comment": "commenting on post"},
    )
    assert response.status_code == 404


def test_comment_post_without_comment(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.post(
        f"/comment/{uuid.uuid4()}",
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 422
    session.close()


def test_comment_post_by_admin(before_admin_login_cred):
    session = create_session()
    token = before_admin_login_cred(session=session)
    response = client.post(
        f"/comment/{uuid.uuid4()}",
        headers=get_auth_header(token=token),
        json={"comment": "commenting on post"},
    )
    assert response.status_code == 403
    session.close()


def test_comment_post_of_private_user_not_followed(
    before_create_private_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_private_user())
    response = client.post(
        f"/comment/{post.id}",
        headers=get_auth_header(token=token),
        json={"comment": "commenting on post"},
    )
    assert response.status_code == 403
    session.refresh(post)
    assert post.comments == []
    session.close()


def test_comment_post_of_private_user_followed(
    before_create_private_user_login_cred,
    before_create_post,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    post = before_create_post(session=session, user_dict=create_private_user())
    before_create_approved_follow_requests(
        session=session, follower_id=user.id, following_id=post.posted_by
    )
    response = client.post(
        f"/comment/{post.id}",
        headers=get_auth_header(token=token),
        json={"comment": "commenting on post"},
    )
    assert response.status_code == 200
    session.refresh(post)
    assert len(post.comments) == 1
    session.close()
