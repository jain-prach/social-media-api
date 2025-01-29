from sqlmodel import select

from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_create_private_user_login_cred,
    before_create_public_user_login_cred,
    before_create_base_user,
    before_create_normal_user,
    before_create_follow_request,
    before_create_approved_follow_requests,
    before_create_private_user_with_followers,
    before_create_public_user_with_followers,
    before_create_private_user_with_following,
    before_create_public_user_with_following,
)
from src.tests.test_utils import (
    create_session,
    get_auth_header,
    create_value_using_session,
)
from src.tests.test_data import create_private_user, create_public_user
from src.application.users.services import JWTService
from src.domain.models import BaseUser, User, FollowersModel
from lib.fastapi.custom_enums import StatusType


def test_list_received_requests(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    before_create_follow_request(
        session=session, follower_id=user1.id, following_id=db_user.user.id
    )
    before_create_follow_request(
        session=session, follower_id=user2.id, following_id=db_user.user.id
    )
    session.close()
    response = client.get(
        "/follow-requests/received/", headers=get_auth_header(token=token)
    )
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 2


def test_list_sent_requests(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    before_create_follow_request(
        session=session, follower_id=db_user.user.id, following_id=user1.id
    )
    before_create_follow_request(
        session=session, follower_id=db_user.user.id, following_id=user2.id
    )
    session.close()
    response = client.get(
        "/follow-requests/sent/", headers=get_auth_header(token=token)
    )
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 2


def test_list_own_followers(
    before_create_public_user_login_cred,
    before_create_normal_user,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    before_create_follow_request(
        session=session, follower_id=user1.id, following_id=db_user.user.id
    )
    username = db_user.user.username
    session.close()
    response = client.post(
        "/followers/", headers=get_auth_header(token=token), json={"username": username}
    )
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 1


def test_list_followers_of_private_user(
    before_create_public_user_login_cred, before_create_private_user_with_followers
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    username = before_create_private_user_with_followers(session=session)
    session.close()
    response = client.post(
        "/followers/", headers=get_auth_header(token=token), json={"username": username}
    )
    assert response.status_code == 403


def test_list_followers_of_private_user_that_is_followed(
    before_create_public_user_login_cred,
    before_create_private_user_with_followers,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    username = before_create_private_user_with_followers(session=session)
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    db_private_user = session.scalars(
        select(User).where(User.username == username)
    ).first()
    before_create_approved_follow_requests(
        session=session, follower_id=db_user.user.id, following_id=db_private_user.id
    )
    session.close()
    response = client.post(
        "/followers/", headers=get_auth_header(token=token), json={"username": username}
    )
    assert response.status_code == 200


def test_list_own_following(
    before_create_public_user_login_cred,
    before_create_normal_user,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user1 = before_create_normal_user(session=session, user_dict=create_public_user())
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    before_create_follow_request(
        session=session, follower_id=db_user.user.id, following_id=user1.id
    )
    username = db_user.user.username
    session.close()
    response = client.post(
        "/following/", headers=get_auth_header(token=token), json={"username": username}
    )
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 1


def test_list_following_of_private_user(
    before_create_public_user_login_cred, before_create_private_user_with_following
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    username = before_create_private_user_with_following(session=session)
    session.close()
    response = client.post(
        "/following/", headers=get_auth_header(token=token), json={"username": username}
    )
    assert response.status_code == 403


def test_list_following_of_private_user_that_is_followed(
    before_create_public_user_login_cred,
    before_create_private_user_with_following,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    username = before_create_private_user_with_following(session=session)
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    db_private_user = session.scalars(
        select(User).where(User.username == username)
    ).first()
    before_create_approved_follow_requests(
        session=session, follower_id=db_user.user.id, following_id=db_private_user.id
    )
    session.close()
    response = client.post(
        "/following/", headers=get_auth_header(token=token), json={"username": username}
    )
    assert response.status_code == 200


def test_send_request(before_create_private_user_login_cred, before_create_normal_user):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    user1 = before_create_normal_user(session=session, user_dict=create_public_user())
    response = client.post(
        "/follow/send/",
        headers=get_auth_header(token=token),
        json={"username": user1.username},
    )
    assert response.status_code == 201
    assert db_user.user in [f.follower for f in user1.followers]
    session.close()


def test_send_request_for_invalid_username(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    session.close()
    response = client.post(
        "/follow/send/",
        headers=get_auth_header(token=token),
        json={"username": "invalid"},
    )
    assert response.status_code == 404


def test_accept_request(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user1 = before_create_normal_user(session=session, user_dict=create_public_user())
    username = user1.username
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    before_create_follow_request(
        session=session, follower_id=user1.id, following_id=db_user.user.id
    )
    response = client.post(
        "/follow/accept/",
        headers=get_auth_header(token=token),
        json={"username": username},
    )
    assert response.status_code == 200
    assert user1.username in [
        f.follower.username
        for f in db_user.user.followers
        if f.status == StatusType.APPROVED.value
    ]
    session.close()


def test_accept_request_for_no_request(
    before_create_private_user_login_cred, before_create_normal_user
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    session.close()
    response = client.post(
        "/follow/accept/",
        headers=get_auth_header(token=token),
        json={"username": user.username},
    )
    assert response.status_code == 400


def test_reject_request(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    username = user.username
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    before_create_follow_request(
        session=session, follower_id=user.id, following_id=db_user.user.id
    )
    response = client.post(
        "/follow/reject/",
        headers=get_auth_header(token=token),
        json={"username": username},
    )
    assert response.status_code == 200
    assert len(db_user.user.followers) == 0
    session.close()


def test_reject_request_for_no_request(
    before_create_private_user_login_cred, before_create_normal_user
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    session.close()
    response = client.post(
        "/follow/reject/",
        headers=get_auth_header(token=token),
        json={"username": user.username},
    )
    assert response.status_code == 400


def test_cancel_request(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    username = user.username
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    before_create_follow_request(
        session=session, follower_id=db_user.user.id, following_id=user.id
    )
    session.close()
    response = client.post(
        "/follow/cancel/",
        headers=get_auth_header(token=token),
        json={"username": username},
    )
    assert response.status_code == 200


def test_cancel_request_for_no_request(
    before_create_private_user_login_cred, before_create_normal_user
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    session.close()
    response = client.post(
        "/follow/cancel/",
        headers=get_auth_header(token=token),
        json={"username": user.username},
    )
    assert response.status_code == 200


def test_unfollow(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    username = user.username
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    before_create_approved_follow_requests(
        session=session, follower_id=db_user.user.id, following_id=user.id
    )
    session.close()
    response = client.post(
        "/follow/unfollow/",
        headers=get_auth_header(token=token),
        json={"username": username},
    )
    assert response.status_code == 200


def test_unfollow_for_no_following(
    before_create_private_user_login_cred, before_create_normal_user
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    username = user.username
    session.close()
    response = client.post(
        "/follow/unfollow/",
        headers=get_auth_header(token=token),
        json={"username": username},
    )
    assert response.status_code == 200


def test_remove_follower(
    before_create_public_user_login_cred,
    before_create_normal_user,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    payload = JWTService().decode(token)
    db_user = session.get(BaseUser, payload.get("id"))
    db_follow = before_create_approved_follow_requests(
        session=session, follower_id=user.id, following_id=db_user.user.id
    )
    username = db_follow.follower.username
    session.close()
    response = client.post(
        "/follow/remove-follower/",
        headers=get_auth_header(token=token),
        json={"username": username},
    )
    assert response.status_code == 200


def test_remove_follower_for_no_follower(
    before_create_public_user_login_cred, before_create_normal_user
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    username = user.username
    session.close()
    response = client.post(
        "/follow/remove-follower/",
        headers=get_auth_header(token=token),
        json={"username": username},
    )
    assert response.status_code == 200


def test_follow_send_request_to_private_user_then_accept_request_and_unfollow(
    before_create_public_user_login_cred, before_create_private_user_login_cred
):
    session = create_session()
    token1 = before_create_public_user_login_cred(session=session)
    token2 = before_create_private_user_login_cred(session=session)
    payload1 = JWTService().decode(token=token1)
    payload2 = JWTService().decode(token=token2)
    user1 = session.scalars(
        select(User).where(User.base_user_id == payload1.get("id"))
    ).first()
    user2 = session.scalars(
        select(User).where(User.base_user_id == payload2.get("id"))
    ).first()
    response = client.post(
        "/follow/send/",
        headers=get_auth_header(token=token1),
        json={"username": user2.username},
    )
    assert response.status_code == 201
    assert user1 in [
        f.follower for f in user2.followers if f.status == StatusType.PENDING.value
    ]
    response = client.post(
        "/follow/accept/",
        headers=get_auth_header(token=token2),
        json={"username": user1.username},
    )
    assert response.status_code == 200
    session.refresh(user2)
    assert user1 in [
        f.follower for f in user2.followers if f.status == StatusType.APPROVED.value
    ]
    response = client.post(
        "/follow/unfollow/",
        headers=get_auth_header(token=token1),
        json={"username": user2.username},
    )
    assert response.status_code == 200
    db_follow = session.scalars(
        select(FollowersModel)
        .where(FollowersModel.follower_id == user1.id)
        .where(FollowersModel.following_id == user2.id)
    ).first()
    assert db_follow is None
    session.close()


def test_follow_send_request_to_private_user_then_reject_request(
    before_create_public_user_login_cred, before_create_private_user_login_cred
):
    session = create_session()
    token1 = before_create_public_user_login_cred(session=session)
    token2 = before_create_private_user_login_cred(session=session)
    payload1 = JWTService().decode(token=token1)
    payload2 = JWTService().decode(token=token2)
    user1 = session.scalars(
        select(User).where(User.base_user_id == payload1.get("id"))
    ).first()
    user2 = session.scalars(
        select(User).where(User.base_user_id == payload2.get("id"))
    ).first()
    response = client.post(
        "/follow/send/",
        headers=get_auth_header(token=token1),
        json={"username": user2.username},
    )
    assert response.status_code == 201
    assert user1 in [
        f.follower for f in user2.followers if f.status == StatusType.PENDING.value
    ]
    response = client.post(
        "/follow/reject/",
        headers=get_auth_header(token=token2),
        json={"username": user1.username},
    )
    assert response.status_code == 200
    db_follow = session.scalars(
        select(FollowersModel)
        .where(FollowersModel.follower_id == user1.id)
        .where(FollowersModel.following_id == user2.id)
    ).first()
    assert db_follow is None
    session.close()