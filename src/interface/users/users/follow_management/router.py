from fastapi import APIRouter

from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from src.interface.auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from lib.fastapi.utils import check_id, only_user_access
from .schemas import (
    FollowRequestSchema,
    FollowRequestSentResponseData,
    FollowRequestListReceivedResponseData,
    FollowRequestListSentResponseData,
    FollowRequestAcceptedResponseData,
    FollowRequestRejectedResponseData,
    FollowRequestCancelledResponseData,
    UnfollowResponseData,
    RemoveFollowerResponseData,
)
from src.application.users.users.follow_management.services import FollowAppService


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
    only_user_access(current_user=current_user)
    follow_app_service = FollowAppService(session=session)
    follow_list = follow_app_service.get_pending_requests_sent_to_user(
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
    only_user_access(current_user=current_user)
    follow_app_service = FollowAppService(session=session)
    follow_list = follow_app_service.get_pending_requests_sent_by_user(
        base_user_id=check_id(id=current_user.get("id"))
    )
    return dict(data=follow_list)


@router.post(
    "ers/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestListReceivedResponseData,
)
def list_followers(current_user: AuthDep, user: FollowRequestSchema, session: SessionDep):
    """list all followers of the user"""
    follow_app_service = FollowAppService(session=session)
    followers = follow_app_service.get_followers(
        current_user=current_user, username=user.username
    )
    return dict(data=followers)


@router.post(
    "ing/", status_code=HTTP_200_OK, response_model=FollowRequestListSentResponseData
)
def list_following(current_user: AuthDep, user: FollowRequestSchema, session: SessionDep):
    """list all users that the user follows"""
    follow_app_service = FollowAppService(session=session)
    following_list = follow_app_service.get_following(
        current_user=current_user, username=user.username
    )
    return dict(data=following_list)


@router.post(
    "/send/", status_code=HTTP_201_CREATED, response_model=FollowRequestSentResponseData
)
def send_request(current_user: AuthDep, user: FollowRequestSchema, session: SessionDep):
    """send request to mentioned user by username"""
    only_user_access(current_user=current_user)
    follow_app_service = FollowAppService(session=session)
    db_follow = follow_app_service.create_follow_request(
        follower_id=check_id(current_user.get("id")), username=user.username
    )
    return dict(data=db_follow)


@router.post(
    "/accept/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestAcceptedResponseData,
)
def accept_request(current_user: AuthDep, user: FollowRequestSchema, session: SessionDep):
    """accept request sent from the mentioned user"""
    only_user_access(current_user=current_user)
    follow_app_service = FollowAppService(session=session)
    follow_app_service.accept_follow_request(
        base_user_id=check_id(id=current_user.get("id")), accept_username=user.username
    )
    return {}


@router.post(
    "/reject/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestRejectedResponseData,
)
def reject_request(current_user: AuthDep, user: FollowRequestSchema, session: SessionDep):
    """reject request sent from the mentioned user"""
    only_user_access(current_user=current_user)
    follow_app_service = FollowAppService(session=session)
    follow_app_service.reject_follow_request(
        base_user_id=check_id(id=current_user.get("id")), reject_username=user.username
    )
    return {}


@router.post(
    "/cancel/",
    status_code=HTTP_200_OK,
    response_model=FollowRequestCancelledResponseData,
)
def cancel_request(current_user: AuthDep, user: FollowRequestSchema, session: SessionDep):
    """cancel request sent to the mentioned user"""
    only_user_access(current_user=current_user)
    follow_app_service = FollowAppService(session=session)
    follow_app_service.cancel_follow_request(
        base_user_id=check_id(id=current_user.get("id")), cancel_username=user.username
    )
    return {}


@router.post(
    "/unfollow/", status_code=HTTP_200_OK, response_model=UnfollowResponseData
)
def unfollow(current_user: AuthDep, user: FollowRequestSchema, session: SessionDep):
    """unfollow mentioned user by current_user"""
    only_user_access(current_user=current_user)
    follow_app_service = FollowAppService(session=session)
    follow_app_service.unfollow(
        base_user_id=check_id(id=current_user.get("id")),
        unfollow_username=user.username,
    )
    return {}


@router.post(
    "/remove_follower/",
    status_code=HTTP_200_OK,
    response_model=RemoveFollowerResponseData,
)
def remove_follower(
    current_user: AuthDep, user: FollowRequestSchema, session: SessionDep
):
    """remove follower of current user"""
    only_user_access(current_user=current_user)
    follow_app_service = FollowAppService(session=session)
    follow_app_service.remove_follower(
        base_user_id=check_id(id=current_user.get("id")),
        remove_username=user.username,
    )
    return {}
