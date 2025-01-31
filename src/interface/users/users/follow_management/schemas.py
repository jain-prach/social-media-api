from typing import List, Optional
import uuid

from pydantic import BaseModel

from lib.fastapi.custom_enums import StatusType
from lib.fastapi.custom_schemas import BaseResponseSchema, BaseResponseNoDataSchema
from src.interface.users.users.schemas import UserResponse, UsernameSchema


class FollowRequestSchema(UsernameSchema):
    """get user by username for follow request operations"""

    pass


class FollowRequestSentResponse(BaseModel):
    """follow request sent response schema"""

    # follower: UserResponse
    following: UserResponse
    status: StatusType


class FollowRequestSentResponseData(BaseResponseSchema):
    """Follow Request Response data with data attribute set to FollowRequestResponse"""

    data: FollowRequestSentResponse


class FollowRequestReceivedResponse(BaseModel):
    """Follow Request received response schema"""

    # id: uuid.UUID
    follower: UserResponse
    # following: UserResponse
    status: StatusType


class FollowRequestListReceivedResponseData(BaseResponseSchema):
    """Follow Request List Received Response data with data attribute to include list of follow request received"""

    data: List[FollowRequestReceivedResponse]


class FollowRequestListSentResponseData(BaseResponseSchema):
    """Follow Request List Sent Response data with data attribute to include list of follow request sent"""

    data: List[FollowRequestSentResponse]


class FollowRequest(BaseModel):
    """schema for database to create follow request"""

    follower_id: uuid.UUID
    following_id: uuid.UUID
    status: StatusType


class FollowRequestAcceptedResponseData(BaseResponseNoDataSchema):
    """Follow Request Accepted Response data with message attribute set to optional static string"""

    message: Optional[str] = "Request Accepted!!"


class FollowRequestRejectedResponseData(BaseResponseNoDataSchema):
    """Follow Request Rejected Response data with message attribute set to optional static string"""

    message: Optional[str] = "Request Rejected!!"


class FollowRequestCancelledResponseData(BaseResponseNoDataSchema):
    """Follow Request Cancelled Response data with message attribute set to optional static string"""

    message: Optional[str] = "Request Cancelled!!"


class UnfollowResponseData(BaseResponseNoDataSchema):
    """Unfollow Response data with message attribute set to optional static string"""

    message: Optional[str] = "User Unfollowed!!"


class RemoveFollowerResponseData(BaseResponseNoDataSchema):
    """Remove Follower Response data with message attribute set to optional static string"""

    message: Optional[str] = "Follower Removed!!"
