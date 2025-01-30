import uuid
from datetime import datetime

from dateutil import relativedelta
import pytest
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from src.tests.test_client import setup_database
from src.tests.test_fixtures import (
    before_create_post,
    before_create_base_user,
    before_create_normal_user,
    before_create_approved_follow_requests,
    before_create_post_caption_search,
    before_create_post_with_different_timestamp,
    before_create_posts_with_multiple_timestamps,
    before_like_post,
)
from src.tests.test_utils import create_session
from src.tests.test_data import (
    create_private_user,
    create_public_user,
    get_user_dict_from_user,
)
from src.domain.posts.services import PostService
from lib.fastapi.custom_enums import FilterDates, ProfileType
from src.domain.models import User, Post


def test_get_post_by_id(before_create_post):
    session = create_session()
    post = before_create_post(session=session, user_dict=create_private_user())
    db_post = PostService(session=session).get_post_by_id(id=post.id)
    assert db_post is not None
    assert db_post.id == post.id


def test_get_post_by_id_for_invalid_post():
    session = create_session()
    db_post = PostService(session=session).get_post_by_id(id=uuid.uuid4())
    assert db_post is None


def test_get_all_posts_by_user_id(before_create_normal_user, before_create_post):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    user_dict = get_user_dict_from_user(user=user)
    before_create_post(session=session, user_dict=user_dict)
    before_create_post(session=session, user_dict=user_dict)
    posts = PostService(session=session).get_all_posts_by_user_id(
        user_id=user.id, search=None, filter_by=None
    )
    assert len(posts) == 2


def test_get_all_posts_by_user_id_for_no_posts_by_user(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    posts = PostService(session=session).get_all_posts_by_user_id(
        user_id=user.id, search=None, filter_by=None
    )
    assert posts == []


def test_get_all_posts_by_user_id_with_search_string(
    before_create_normal_user, before_create_post, before_create_post_caption_search
):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    user_dict = get_user_dict_from_user(user=user)
    for i in range(10):
        if i < 5:
            before_create_post(session=session, user_dict=user_dict)
        else:
            before_create_post_caption_search(session=session, user_dict=user_dict)
    posts = PostService(session=session).get_all_posts_by_user_id(
        user_id=user.id, search="search", filter_by=None
    )
    assert len(posts) == 5


def test_get_all_posts_by_user_id_with_search_string_with_other_user_same_caption(
    before_create_normal_user, before_create_post, before_create_post_caption_search
):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    user_dict = get_user_dict_from_user(user=user)
    before_create_post_caption_search(session=session, user_dict=create_private_user())
    for i in range(10):
        if i < 5:
            before_create_post(session=session, user_dict=user_dict)
        else:
            before_create_post_caption_search(session=session, user_dict=user_dict)
    posts = PostService(session=session).get_all_posts_by_user_id(
        user_id=user.id, search="search", filter_by=None
    )
    assert len(posts) == 5


def test_get_all_posts_by_user_id_with_search_string_with_no_post(
    before_create_normal_user, before_create_post
):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    user_dict = get_user_dict_from_user(user=user)
    before_create_post(session=session, user_dict=user_dict)
    posts = PostService(session=session).get_all_posts_by_user_id(
        user_id=user.id, search="search", filter_by=None
    )
    assert posts == []


def test_get_all_posts_by_user_id_filtered_by_this_month_timestamp(
    before_create_normal_user, before_create_posts_with_multiple_timestamps
):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    user_dict = get_user_dict_from_user(user=user)
    before_create_posts_with_multiple_timestamps(session=session, user_dict=user_dict)
    posts = PostService(session=session).get_all_posts_by_user_id(
        user_id=user.id, search=None, filter_by=FilterDates.THIS_MONTH.value
    )
    assert len(posts) == 2


# ASK: check why every posts is getting created at 30-12 instead
# def test_get_all_posts_by_user_id_filtered_by_last_six_months_timestamp(
#     before_create_normal_user, before_create_posts_with_multiple_timestamps
# ):
#     session = create_session()
#     user = before_create_normal_user(session=session, user_dict=create_private_user())
#     user_dict = get_user_dict_from_user(user=user)
#     before_create_posts_with_multiple_timestamps(session=session, user_dict=user_dict)
#     posts = PostService(session=session).get_all_posts_by_user_id(
#         user_id=user.id, search=None, filter_by=FilterDates.LAST_SIX_MONTHS.value
#     )
#     assert len(posts) == 4


# def test_get_all_posts_by_user_id_filtered_by_last_one_year_timestamp(
#     before_create_normal_user, before_create_posts_with_multiple_timestamps
# ):
#     session = create_session()
#     user = before_create_normal_user(session=session, user_dict=create_private_user())
#     user_dict = get_user_dict_from_user(user=user)
#     before_create_posts_with_multiple_timestamps(session=session, user_dict=user_dict)
#     posts = PostService(session=session).get_all_posts_by_user_id(
#         user_id=user.id, search=None, filter_by=FilterDates.LAST_ONE_YEAR.value
#     )
#     assert len(posts) == 6


# def test_get_all_posts_by_user_id_filtered_by_last_ten_years_timestamp(
#     before_create_normal_user, before_create_posts_with_multiple_timestamps
# ):
#     session = create_session()
#     user = before_create_normal_user(session=session, user_dict=create_private_user())
#     user_dict = get_user_dict_from_user(user=user)
#     before_create_posts_with_multiple_timestamps(session=session, user_dict=user_dict)
#     posts = PostService(session=session).get_all_posts_by_user_id(
#         user_id=user.id, search=None, filter_by=FilterDates.LAST_TEN_YEARS.value
#     )
#     assert len(posts) == 8

# WRITE FOR SEARCH AND FILTER BY


def test_get_all_posts_not_liked_by_user(before_create_post, before_like_post):
    session = create_session()

    # create post by public and private user not followed
    for i in range(10):
        if i < 5:
            before_create_post(session=session, user_dict=create_public_user())
        else:
            before_create_post(session=session, user_dict=create_private_user())

    # like post
    db_like = before_like_post(
        session=session, posted_by=create_public_user(), liked_by=create_private_user()
    )
    liked_post = db_like.post

    # get user that liked the post
    liked_by = session.get(User, db_like.liked_by)

    # creating a post by the user who liked
    user_post = before_create_post(
        session=session,
        user_dict=get_user_dict_from_user(user=liked_by),
    )

    # public users
    public_users = session.exec(
        select(User).where(User.profile_type == ProfileType.PUBLIC)
    ).all()

    # get posts
    posts = PostService(session=session).get_all_posts_not_liked_by_user(
        user=liked_by,
        public_users=public_users,
    )

    # total posts = 12 -> should get 5
    assert liked_post not in posts
    assert user_post not in posts
    assert len(posts) == 5


def test_get_all_posts_not_liked_by_user_for_private_user_followed(
    before_create_normal_user,
    before_create_post,
    before_like_post,
    before_create_approved_follow_requests,
):
    session = create_session()

    private_user = before_create_normal_user(
        session=session, user_dict=create_private_user()
    )

    # create post by public and private user not followed
    for i in range(10):
        if i < 5:
            before_create_post(session=session, user_dict=create_public_user())
        else:
            before_create_post(
                session=session, user_dict=get_user_dict_from_user(user=private_user)
            )

    # like post
    db_like = before_like_post(
        session=session, posted_by=create_public_user(), liked_by=create_private_user()
    )
    liked_post = db_like.post

    # get user that liked the post
    liked_by = session.get(User, db_like.liked_by)

    # creating a post by the user who liked
    user_post = before_create_post(
        session=session,
        user_dict=get_user_dict_from_user(user=liked_by),
    )

    # public users
    public_users = session.exec(
        select(User).where(User.profile_type == ProfileType.PUBLIC)
    ).all()

    # follow private user
    before_create_approved_follow_requests(
        session=session, follower_id=liked_by.id, following_id=private_user.id
    )

    # get posts
    posts = PostService(session=session).get_all_posts_not_liked_by_user(
        user=liked_by,
        public_users=public_users,
    )

    # total posts = 12 -> should get 10
    assert liked_post not in posts
    assert user_post not in posts
    assert len(posts) == 10


def test_create(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    db_post = PostService(session=session).create(
        post={"posted_by": user.id, "caption": "caption text"}
    )
    assert db_post is not None
    assert db_post.posted_by == user.id


def test_create_with_invalid_user():
    session = create_session()
    with pytest.raises(IntegrityError):
        PostService(session=session).create(
            post={"posted_by": uuid.uuid4(), "caption": "caption text"}
        )


def test_create_without_posted_by():
    session = create_session()
    with pytest.raises(ValidationError):
        PostService(session=session).create(post={"caption": "caption text"})


def test_create_without_caption(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    db_post = PostService(session=session).create(post={"posted_by": user.id})
    assert db_post is not None
    assert db_post.posted_by == user.id


def test_update(before_create_normal_user, before_create_post):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    post = before_create_post(session=session, user_dict=create_private_user())
    new_caption = "new caption text"
    db_post = PostService(session=session).update(
        post={"posted_by": user.id, "caption": new_caption}, db_post=post
    )
    assert db_post is not None
    assert db_post.posted_by == user.id
    assert db_post.caption == new_caption


def test_update_with_invalid_user_id(before_create_post):
    session = create_session()
    post = before_create_post(session=session, user_dict=create_private_user())
    new_caption = "new caption text"
    with pytest.raises(IntegrityError):
        PostService(session=session).update(
            post={"posted_by": uuid.uuid4(), "caption": new_caption}, db_post=post
        )


def test_update_without_caption(before_create_normal_user, before_create_post):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    post = before_create_post(session=session, user_dict=create_private_user())
    db_post = PostService(session=session).update(
        post={"posted_by": user.id}, db_post=post
    )
    assert db_post is not None
    assert db_post.posted_by == user.id
    assert db_post.caption == post.caption

def test_update_without_user_id(before_create_post):
    session = create_session()
    post = before_create_post(session=session, user_dict=create_private_user())
    new_caption = "new caption text"
    db_post = PostService(session=session).update(
        post={"caption": new_caption}, db_post=post
    )
    assert db_post is not None
    assert db_post.posted_by == post.posted_by
    assert db_post.caption == new_caption

def test_delete(before_create_post):
    session = create_session()
    db_post = before_create_post(session=session, user_dict=create_private_user())
    PostService(session=session).delete(db_post=db_post)
    post = session.get(Post, db_post.id)
    assert post is None
