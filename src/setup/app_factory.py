from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi_pagination.utils import disable_installed_extensions_check
from fastapi.exceptions import RequestValidationError

from src.interface.auth.router import router as auth_router
from src.interface.users.router import router as base_user_router
from src.interface.users.users.router import router as user_router
from src.interface.users.admins.router import router as admin_router
from src.interface.users.users.follow_management.router import router as follow_router
from src.interface.posts.router import router as post_router
from src.interface.posts.likes.router import router as likes_router
from src.interface.posts.comments.router import router as comments_router
from src.interface.posts.reported_posts.router import router as report_post_router
from src.interface.payments.subscription.router import router as subscription_router
from lib.fastapi.custom_middlewares import HandleExceptionMiddleware
from lib.fastapi.utils import get_pydantic_error_response

disable_installed_extensions_check()

app = FastAPI()


def pydantic_exception_handler(request: Request, exc: RequestValidationError):
    return get_pydantic_error_response(e=exc)


app.add_exception_handler(
    exc_class_or_status_code=RequestValidationError, handler=pydantic_exception_handler
)

app.add_middleware(HandleExceptionMiddleware)
app.include_router(auth_router)
app.include_router(base_user_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(follow_router)
app.include_router(post_router)
app.include_router(likes_router)
app.include_router(comments_router)
app.include_router(report_post_router)
app.include_router(subscription_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Social Media API",
        version="1.0.0",
        summary="Social Media API with authentication, payment, profile upload, user following and post upload",
        routes=app.routes,
    )
    # customize here
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
# print(app.openapi()["paths"]["/user/"]['put']["requestBody"]["content"]["multipart/form-data"]["schema"])
