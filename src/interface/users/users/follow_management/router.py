from fastapi import APIRouter

from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from src.interface.auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from lib.fastapi.utils import check_id
from lib.fastapi.error_string import get_admin_not_allowed
from lib.fastapi.custom_enums import Role
from lib.fastapi.custom_exceptions import UnauthorizedException
from .schemas import (
    SendRequestSchema,
    FollowRequestSentResponseData,
    FollowRequestListReceivedResponseData,
    FollowRequestListSentResponseData,
    FollowRequestAcceptedResponseData,
    FollowRequestRejectedResponseData,
    FollowRequestCancelledResponseData,
    UnfollowUserResponseData,
    RemoveFollowerResponseData,
)
from src.application.users.users.follow_management.services import FollowerAppService


router = APIRouter(
    prefix="/follow", tags=["follow"], route_class=UniqueConstraintErrorRoute
)


@router.get(
    "-requests/received/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestListReceivedResponseData,
)
def list_received_requests(current_user: AuthDep, session: SessionDep):
    """list pending requests sent to the user"""
    if current_user.get("role") == Role.ADMIN.value:
        raise UnauthorizedException(get_admin_not_allowed())
    follow_list = FollowerAppService(session=session).get_pending_requests_sent_to_user(
        base_user_id=check_id(id=current_user.get("id"))
    )
    return dict(data=follow_list)


@router.get(
    "-requests/sent/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestListSentResponseData,
)
def list_sent_requests(current_user: AuthDep, session: SessionDep):
    """list pending requests sent by the user"""
    if current_user.get("role") == Role.ADMIN.value:
        raise UnauthorizedException(get_admin_not_allowed())
    follow_list = FollowerAppService(session=session).get_pending_requests_sent_by_user(
        base_user_id=check_id(id=current_user.get("id"))
    )
    return dict(data=follow_list)


@router.get(
    "ers/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestListReceivedResponseData,
)
def list_followers(current_user: AuthDep, username: str, session: SessionDep):
    """list all followers of the user"""
    followers = FollowerAppService(session=session).get_followers(
        current_user_id=check_id(id=current_user.get("id")), username=username
    )
    return dict(data=followers)


@router.get(
    "ing/", status_code=HTTP_200_OK, response_model=FollowRequestListSentResponseData
)
def list_following(current_user: AuthDep, username: str, session: SessionDep):
    """list all users that the user follows"""
    following_list = FollowerAppService(session=session).get_following(
        current_user_id=check_id(id=current_user.get("id")), username=username
    )
    return dict(data=following_list)


@router.post(
    "/send/", status_code=HTTP_201_CREATED, response_model=FollowRequestSentResponseData
)
def send_request(current_user: AuthDep, user: SendRequestSchema, session: SessionDep):
    """send request to mentioned user by username"""
    if current_user.get("role") == Role.ADMIN.value:
        raise UnauthorizedException(get_admin_not_allowed())
    follow = FollowerAppService(session=session).create_follow_request(
        follower_id=check_id(current_user.get("id")), username=user.username
    )
    return dict(data=follow)


@router.post(
    "/accept/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestAcceptedResponseData,
)
def accept_request(current_user: AuthDep, user: SendRequestSchema, session: SessionDep):
    """accept request sent from the mentioned user"""
    if current_user.get("role") == Role.ADMIN.value:
        raise UnauthorizedException(get_admin_not_allowed())
    FollowerAppService(session=session).accept_follow_request(
        base_user_id=check_id(id=current_user.get("id")), accept_username=user.username
    )
    return FollowRequestAcceptedResponseData()


@router.post(
    "/reject/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestAcceptedResponseData,
)
def reject_request(current_user: AuthDep, user: SendRequestSchema, session: SessionDep):
    """reject request sent from the mentioned user"""
    if current_user.get("role") == Role.ADMIN.value:
        raise UnauthorizedException(get_admin_not_allowed())
    FollowerAppService(session=session).reject_follow_request(
        base_user_id=check_id(id=current_user.get("id")), reject_username=user.username
    )
    return FollowRequestRejectedResponseData()


@router.post(
    "/cancel/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestCancelledResponseData,
)
def cancel_request(current_user: AuthDep, user: SendRequestSchema, session: SessionDep):
    """cancel request sent to the mentioned user"""

    FollowerAppService(session=session).cancel_follow_request(
        base_user_id=check_id(id=current_user.get("id")), cancel_username=user.username
    )
    return FollowRequestCancelledResponseData()


@router.post(
    "/unfollow/", status_code=HTTP_200_OK, response_model=UnfollowUserResponseData
)
def unfollow_user(current_user: AuthDep, user: SendRequestSchema, session: SessionDep):
    """unfollow mentioned user by current_user"""
    FollowerAppService(session=session).unfollow_user(
        base_user_id=check_id(id=current_user.get("id")),
        unfollow_username=user.username,
    )
    return UnfollowUserResponseData()


@router.post(
    "/remove_follower/",
    status_code=HTTP_200_OK,
    response_model=RemoveFollowerResponseData,
)
def remove_follower(
    current_user: AuthDep, user: SendRequestSchema, session: SessionDep
):
    """remove follower of current user"""
    FollowerAppService(session=session).remove_follower(
        base_user_id=check_id(id=current_user.get("id")),
        remove_username=user.username,
    )
    return RemoveFollowerResponseData()
