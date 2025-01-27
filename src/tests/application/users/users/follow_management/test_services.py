import uuid

from sqlmodel import select
import pytest

from src.domain.models import FollowersModel, User
from src.application.users.services import JWTService
from src.application.users.users.follow_management.services import FollowAppService
from src.tests.test_utils import create_session
from src.tests.test_fixtures import (
    before_create_base_user,
    before_create_normal_user,
    before_create_follow_request,
    before_create_approved_follow_requests,
    before_create_follow,
    before_create_private_user_with_followers,
    before_create_public_user_with_followers,
    before_create_private_user_with_following,
    before_create_public_user_with_following,
    before_create_private_user_login_cred,
)
from src.tests.test_client import setup_database
from src.tests.test_data import create_public_user, create_private_user, get_username
from lib.fastapi.custom_enums import StatusType, ProfileType
from lib.fastapi.custom_exceptions import BadRequestException, ForbiddenException


def test_get_follow_by_follow_id(before_create_follow):
    session = create_session()
    db_follow = before_create_follow(session=session)
    output = FollowAppService(session=session).get_follow_by_follow_id(id=db_follow.id)
    assert output.id == db_follow.id
    assert isinstance(output, FollowersModel)
    session.close()


def test_get_follow_for_invalid_id():
    session = create_session()
    output = FollowAppService(session=session).get_follow_by_follow_id(id=uuid.uuid4())
    assert output is None
    session.close()


def test_get_user_by_base_user_id(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    output = FollowAppService(session=session).get_user_by_base_user_id(
        base_user_id=user.base_user_id
    )
    assert output.id == user.id
    assert isinstance(output, User)
    session.close()


def test_get_user_by_base_user_id_for_no_user():
    session = create_session()
    with pytest.raises(BadRequestException):
        FollowAppService(session=session).get_user_by_base_user_id(
            base_user_id=uuid.uuid4()
        )
    session.close()


def test_get_user_by_username(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_public_user())
    output = FollowAppService(session=session).get_user_by_username(
        username=user.username
    )
    assert output.id == user.id
    assert isinstance(output, User)
    session.close()


def test_get_user_by_username_for_no_user():
    session = create_session()
    with pytest.raises(BadRequestException):
        FollowAppService(session=session).get_user_by_username(username=get_username())
    session.close()


def test_get_all_followers(before_create_private_user_with_followers):
    session = create_session()
    username = before_create_private_user_with_followers(session=session)
    user = session.scalars(select(User).where(User.username == username)).first()
    output = FollowAppService(session=session).get_all_followers(
        base_user_id=user.base_user_id
    )
    assert len(output) == 1
    assert isinstance(output[0], FollowersModel)
    session.close()


def test_get_all_following_list(before_create_private_user_with_following):
    session = create_session()
    username = before_create_private_user_with_following(session=session)
    user = session.scalars(select(User).where(User.username == username)).first()
    output = FollowAppService(session=session).get_all_following_list(
        base_user_id=user.base_user_id
    )
    assert len(output) == 1
    assert isinstance(output[0], FollowersModel)
    session.close()


def test_get_pending_requests_sent_to_user(
    before_create_follow_request, before_create_normal_user
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_public_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_follow_request(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    output = FollowAppService(session=session).get_pending_requests_sent_to_user(
        base_user_id=user2.base_user_id
    )
    assert len(output) == 1
    assert isinstance(output[0], FollowersModel)
    assert output[0].following_id == user2.id
    assert output[0].status == StatusType.PENDING.value
    session.close()


def test_get_pending_requests_sent_by_user(
    before_create_follow_request, before_create_normal_user
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_public_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_follow_request(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    output = FollowAppService(session=session).get_pending_requests_sent_by_user(
        base_user_id=user1.base_user_id
    )
    assert len(output) == 1
    assert isinstance(output[0], FollowersModel)
    assert output[0].follower_id == user1.id
    assert output[0].status == StatusType.PENDING.value
    session.close()


def test_get_followers(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_approved_follow_requests,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    payload = JWTService().decode(token=token)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_user = session.scalars(
        select(User).where(User.base_user_id == payload.get("id"))
    ).first()
    before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=db_user.id
    )
    before_create_follow_request(
        session=session, follower_id=user2.id, following_id=db_user.id
    )
    # own
    output = FollowAppService(session=session).get_followers(
        current_user=payload, username=db_user.username
    )
    assert len(output) == 1
    assert isinstance(output[0], FollowersModel)
    assert output[0].following_id == db_user.id
    assert output[0].status == StatusType.APPROVED.value
    session.close()


def test_get_followers_for_private_user_not_followed(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    payload = JWTService().decode(token=token)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    with pytest.raises(ForbiddenException):
        FollowAppService(session=session).get_followers(
            current_user=payload, username=user2.username
        )
    session.close()


def test_get_following(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_approved_follow_requests,
    before_create_follow_request,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    payload = JWTService().decode(token=token)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_user = session.scalars(
        select(User).where(User.base_user_id == payload.get("id"))
    ).first()
    before_create_approved_follow_requests(
        session=session, follower_id=db_user.id, following_id=user1.id
    )
    before_create_follow_request(
        session=session, follower_id=db_user.id, following_id=user2.id
    )
    # own
    output = FollowAppService(session=session).get_following(
        current_user=payload, username=db_user.username
    )
    assert len(output) == 1
    assert isinstance(output[0], FollowersModel)
    assert output[0].follower_id == db_user.id
    assert output[0].status == StatusType.APPROVED.value
    session.close()

def test_get_following_for_private_user_not_followed(
    before_create_private_user_login_cred,
    before_create_normal_user,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    payload = JWTService().decode(token=token)
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    with pytest.raises(ForbiddenException):
        FollowAppService(session=session).get_followers(
            current_user=payload, username=user1.username
        )
    session.close()


def test_send_request(before_create_normal_user):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_public_user())
    output = FollowAppService(session=session).send_request(follower=user1, user=user2)
    assert isinstance(output, FollowersModel)
    assert output.follower_id == user1.id
    assert output.following_id == user2.id
    if user2.profile_type == ProfileType.PRIVATE.value:
        assert output.status == StatusType.PENDING.value
    session.close()


def test_create_follower(before_create_normal_user):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    output = FollowAppService(session=session).create_follower(
        follower=user1, user=user2
    )
    assert isinstance(output, FollowersModel)
    assert output.follower_id == user1.id
    assert output.following_id == user2.id
    assert output.status == StatusType.APPROVED.value
    session.close()


def test_create_follow_request(before_create_normal_user):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    output = FollowAppService(session=session).create_follow_request(
        follower_base_user_id=user1.base_user_id, username=user2.username
    )
    assert isinstance(output, FollowersModel)
    assert output.follower_id == user1.id
    assert output.following_id == user2.id
    if user2.profile_type == ProfileType.PRIVATE.value:
        assert output.status == StatusType.PENDING.value
    else:
        assert output.status == StatusType.APPROVED.value
    session.close()


def test_accept_follow_request(before_create_normal_user, before_create_follow_request):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_follow_request(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    output = FollowAppService(session=session).accept_follow_request(
        base_user_id=user2.base_user_id, accept_username=user1.username
    )
    assert isinstance(output, FollowersModel)
    assert output.follower_id == user1.id
    assert output.following_id == user2.id
    assert output.status == StatusType.APPROVED.value
    session.close()


def test_reject_follow_request(before_create_normal_user, before_create_follow_request):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_follow_request(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    output = FollowAppService(session=session).reject_follow_request(
        base_user_id=user2.base_user_id, reject_username=user1.username
    )
    assert output is None
    db_follow = session.scalars(
        select(FollowersModel)
        .where(FollowersModel.follower_id == user1.id)
        .where(FollowersModel.following_id == user2.id)
    ).first()
    assert db_follow is None
    session.close()


def test_cancel_follow_request(before_create_normal_user, before_create_follow_request):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_follow_request(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    output = FollowAppService(session=session).cancel_follow_request(
        base_user_id=user1.base_user_id, cancel_username=user2.username
    )
    assert output is None
    db_follow = session.scalars(
        select(FollowersModel)
        .where(FollowersModel.follower_id == user1.id)
        .where(FollowersModel.following_id == user2.id)
    ).first()
    assert db_follow is None
    session.close()


def test_unfollow(before_create_normal_user, before_create_approved_follow_requests):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    output = FollowAppService(session=session).unfollow(
        base_user_id=user1.base_user_id, unfollow_username=user2.username
    )
    assert output is None
    db_follow = session.scalars(
        select(FollowersModel)
        .where(FollowersModel.follower_id == user1.id)
        .where(FollowersModel.following_id == user2.id)
    ).first()
    assert db_follow is None
    session.close()


def test_remove_follower(
    before_create_normal_user, before_create_approved_follow_requests
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    output = FollowAppService(session=session).remove_follower(
        base_user_id=user2.base_user_id, remove_username=user1.username
    )
    assert output is None
    db_follow = session.scalars(
        select(FollowersModel)
        .where(FollowersModel.follower_id == user1.id)
        .where(FollowersModel.following_id == user2.id)
    ).first()
    assert db_follow is None
    session.close()
