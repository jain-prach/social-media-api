from typing import Optional

from pydantic import BaseModel
from starlette.status import HTTP_200_OK


class BaseResponseSchema(BaseModel):
    """base response schema"""
    message: Optional[str] = "success"
    status: Optional[int] = HTTP_200_OK


# class BaseResponse:
#     """
#     customized data response

#     Attributes
#         message : Optional[str]
#         data : Optional[BaseModel]
#             pydantic response model
#         status : Optional[int]
#     """

#     def __init__(
#         self,
#         message: Optional[str] = None,
#         data: Optional[BaseModel] = None,
#         status: Optional[int] = None,
#     ):
#         self.message = str(message) if message else None
#         self.data = data if data else {}
#         self.status = status

#     @property
#     def status_text(self):
#         """
#         Returns reason text corresponding to our HTTP response status code.
#         Provided for convenience.
#         """
#         return responses.get(int(self.status_code), "")

#     def success_message(self):
#         """returns success response"""
#         self.status_code = self.status if self.status else HTTP_200_OK
#         self.message = self.message if self.message else "success"
#         return BaseResponseSchema(
#             message=self.message, data=self.data, status=self.status_text
#         )

#     def error_message(self):
#         """returns error response"""
#         self.status_code = self.status if self.status else HTTP_400_BAD_REQUEST
#         self.message = self.message if self.message else "error"
#         return BaseResponseSchema(
#             message=self.message, data=self.data, status=self.status_text
#         )
