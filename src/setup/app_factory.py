from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi_pagination.utils import disable_installed_extensions_check
from fastapi.exceptions import RequestValidationError
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

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
from lib.fastapi.custom_middlewares import HandleExceptionMiddleware, CustomTrustedHostMiddleware
from lib.fastapi.custom_exceptions import rate_limit_exceeded_handler
from lib.fastapi.utils import get_pydantic_error_response
# from src.setup.config.logs import get_logger
from src.setup.config.settings import settings
from src.setup.config.limiter import limiter

# logger = get_logger(__name__)

disable_installed_extensions_check()

app = FastAPI()
app.state.limiter = limiter

def pydantic_exception_handler(request: Request, exc: RequestValidationError):
    return get_pydantic_error_response(e=exc)

app.add_exception_handler(
    exc_class_or_status_code=RequestValidationError, handler=pydantic_exception_handler
)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(HandleExceptionMiddleware)
# app.add_middleware(CustomResponseCSRFMiddleware, secret=settings.STARLETTE_CSRF_SECRET)
app.add_middleware(CustomTrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(SlowAPIMiddleware)
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
    """customizing schema"""
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
