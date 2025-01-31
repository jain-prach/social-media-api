import uuid

from sqlmodel import select

from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_create_private_user_login_cred,
    before_create_public_user_login_cred,
    before_create_normal_user,
    before_create_post,
    before_create_base_user,
    before_create_approved_follow_requests,
    before_create_post_with_different_timestamp,
    before_create_post_caption_search,
    before_create_subscription,
)
from src.tests.test_data import create_public_user, create_private_user, get_username
from src.tests.test_utils import create_session, get_auth_header, get_user_by_token
from src.domain.models import BaseUser, User, Post
from src.application.users.services import JWTService
from src.setup.config.settings import settings


def test_list_posts_unauthorized_access_not_allowed():
    response = client.get(f"/posts/{get_username()}/")
    assert response.status_code == 401


def test_list_posts_for_public_user(
    before_create_private_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_public_user())
    user = session.get(User, post.posted_by)
    session.close()
    response = client.get(
        f"/posts/{user.username}/", headers=get_auth_header(token=token)
    )
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data["items"]) == 1


def test_list_posts_for_private_user(
    before_create_public_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_private_user())
    user = session.get(User, post.posted_by)
    response = client.get(
        f"/posts/{user.username}/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 403
    session.close()


def test_list_posts_for_private_user_that_is_followed(
    before_create_public_user_login_cred,
    before_create_post,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    post = before_create_post(session=session, user_dict=create_private_user())
    user1 = session.get(User, post.posted_by)
    before_create_approved_follow_requests(
        session=session, follower_id=user.id, following_id=user1.id
    )
    response = client.get(
        f"/posts/{user1.username}/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 1
    session.close()


def test_list_posts_pagination(
    before_create_public_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = create_public_user()
    for i in range(10):
        before_create_post(session=session, user_dict=user)
    response = client.get(
        f"/posts/{user['username']}/?page=2", headers=get_auth_header(token=token)
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == settings.POST_PAGINATION_SIZE
    assert data["page"] == 2
    session.close()


def test_list_posts_filter_by_dates(
    before_create_public_user_login_cred,
    before_create_post,
    before_create_post_with_different_timestamp,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = create_public_user()
    for i in range(10):
        if i < 5:
            before_create_post(session=session, user_dict=user)
        else:
            before_create_post_with_different_timestamp(session=session, user_dict=user)

    response = client.get(
        f"/posts/{user['username']}/?filter_by=this-month",
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 5


def test_list_posts_filter_by_dates_with_invalid_filter_value(
    before_create_public_user_login_cred,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = create_public_user()
    response = client.get(
        f"/posts/{user['username']}/?filter_by=invalid",
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 422


def test_list_posts_search(
    before_create_public_user_login_cred,
    before_create_post,
    before_create_post_caption_search,
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = create_public_user()
    for i in range(10):
        if i < 5:
            before_create_post(session=session, user_dict=user)
        else:
            before_create_post_caption_search(session=session, user_dict=user)
    response = client.get(
        f"/posts/{user['username']}/?search=search",
        headers=get_auth_header(token=token),
    )
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["total"] == 5


def test_create_post(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.post(
            "post/",
            headers=get_auth_header(token),
            data={"caption": "caption for post"},
            files=[("media", f), ("media", f)],
        )
    data = response.json()["data"]
    assert response.status_code == 201
    assert len(data["media"]) == 2
    db_post = session.get(Post, data["id"])
    assert db_post is not None
    session.close()


def test_create_post_with_unauthorized_access():
    response = client.post(
        "post/",
        data={"caption": "caption for post"},
    )
    assert response.status_code == 401


def test_create_post_without_media(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    response = client.post(
        "post/",
        headers=get_auth_header(token),
        data={"caption": "caption for post"},
    )
    assert response.status_code == 422


def test_create_post_without_caption(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.post(
            "post/",
            headers=get_auth_header(token),
            files=[("media", f), ("media", f)],
        )
    data = response.json()["data"]
    assert response.status_code == 201
    assert len(data["media"]) == 2
    db_post = session.get(Post, data["id"])
    assert db_post is not None
    assert db_post.caption is None
    session.close()


def test_create_post_with_whitespaces_caption(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    caption = "        caption for post          "
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.post(
            "post/",
            headers=get_auth_header(token),
            data={"caption": caption},
            files=[("media", f), ("media", f)],
        )
    data = response.json()["data"]
    assert response.status_code == 201
    assert len(data["media"]) == 2
    db_post = session.get(Post, data["id"])
    assert db_post is not None
    assert db_post.caption == caption.strip()
    session.close()


def test_update_post(before_create_public_user_login_cred, before_create_post):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    post = before_create_post(
        session=session,
        user_dict={
            "username": user.username,
            "bio": user.bio,
            "profile_type": user.profile_type,
        },
    )
    caption = "New Updated Caption!"
    post_id = post.id
    session.close()
    response = client.put(
        f"/post/{post_id}/",
        params={"caption": caption},  # why is data not allowed here?
        headers=get_auth_header(token=token),
    )
    data = response.json()["data"]
    assert response.status_code == 200
    assert data["caption"] == caption
    session = create_session()
    db_post = session.get(Post, post_id)
    assert db_post.caption == caption
    session.close()


def test_update_post_with_unauthorized_access():
    response = client.put(
        f"/post/{uuid.uuid4()}/",
    )
    assert response.status_code == 401


def test_update_post_without_caption(
    before_create_public_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    post = before_create_post(
        session=session,
        user_dict={
            "username": user.username,
            "bio": user.bio,
            "profile_type": user.profile_type,
        },
    )
    response = client.put(
        f"/post/{post.id}/",
        headers=get_auth_header(token=token),
    )
    session.close()
    assert response.status_code == 422


def test_update_post_for_no_post_created(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    caption = "New Updated Caption!"
    response = client.put(
        f"/post/{uuid.uuid4()}/",
        params={"caption": caption},
        headers=get_auth_header(token=token),
    )
    session.close()
    assert response.status_code == 404


def test_update_post_of_another_user(
    before_create_public_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    caption = "New Updated Caption!"
    post = before_create_post(session=session, user_dict=create_public_user())
    response = client.put(
        f"/post/{post.id}/",
        params={"caption": caption},
        headers=get_auth_header(token=token),
    )
    session.close()
    assert response.status_code == 404


def test_delete_post(before_create_public_user_login_cred, before_create_post):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    post = before_create_post(
        session=session,
        user_dict={
            "username": user.username,
            "bio": user.bio,
            "profile_type": user.profile_type,
        },
    )
    post_id = post.id
    session.close()
    response = client.delete(f"/post/{post_id}/", headers=get_auth_header(token=token))
    assert response.status_code == 200
    session = create_session()
    db_post = session.get(Post, post_id)
    assert db_post is None
    session.close()


def test_delete_post_with_unauthorized_access():
    response = client.delete(
        f"/post/{uuid.uuid4()}/",
    )
    assert response.status_code == 401


def test_delete_post_for_no_post_created(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    session.close()
    response = client.delete(
        f"/post/{uuid.uuid4()}/", headers=get_auth_header(token=token)
    )
    assert response.status_code == 200


def test_delete_post_of_another_user(
    before_create_public_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_public_user())
    response = client.delete(f"/post/{post.id}/", headers=get_auth_header(token=token))
    assert response.status_code == 200
    session.refresh(post)
    db_post = session.get(Post, post.id)
    assert db_post is not None
    session.close()


def test_create_ad_without_payment(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.post(
            "post/ad/",
            headers=get_auth_header(token),
            data={"caption": "caption for post"},
            files=[("media", f)],
        )
    assert response.status_code == 403


def test_create_ad_after_payment(
    before_create_public_user_login_cred, before_create_subscription
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    before_create_subscription(session=session, user=user)
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.post(
            "post/ad/",
            headers=get_auth_header(token),
            data={"caption": "caption for post"},
            files=[("media", f)],
        )
    assert response.status_code == 201


def test_create_ad_with_unauthorized_access():
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.post(
            "post/ad/",
            data={"caption": "caption for post"},
            files=[("media", f)],
        )
    assert response.status_code == 401


def test_create_ad_without_caption(
    before_create_public_user_login_cred, before_create_subscription
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    before_create_subscription(session=session, user=user)
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.post(
            "post/ad/",
            headers=get_auth_header(token),
            files=[("media", f)],
        )
    assert response.status_code == 201


def test_create_ad_without_media(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    response = client.post(
        "post/ad/",
        headers=get_auth_header(token),
        data={"caption": "caption for post"},
    )
    assert response.status_code == 422
