from typing import List, Optional
import uuid

from pydantic import BaseModel

from lib.fastapi.custom_enums import StatusType
from lib.fastapi.custom_schemas import BaseResponseSchema
from src.interface.users.users.schemas import UserResponse


class SendRequestSchema(BaseModel):
    """send request to user"""

    username: str


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

    id: uuid.UUID
    follower: UserResponse
    # following: UserResponse
    status: StatusType


class FollowRequestListReceivedResponseData(BaseResponseSchema):
    """Follow Request List Received Response data with data attribute to include list of follow request received"""

    data: List[FollowRequestReceivedResponse]


class FollowRequestListSentResponseData(BaseResponseSchema):
    """Follow Request List Sent Response data with data attribute to include list of follow request sent"""

    data: List[FollowRequestSentResponse]

class FollowRequestAcceptedResponseData(BaseResponseSchema):
    """Follow Request Accepted Response data with data attribute set to static string"""
    
    data: Optional[str] = "Request Accepted!!"