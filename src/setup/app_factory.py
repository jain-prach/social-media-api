from fastapi import FastAPI

from fastapi_pagination.utils import disable_installed_extensions_check

from src.interface.auth.router import router as auth_router
from src.interface.users.router import router as base_user_router
from src.interface.users.users.router import router as user_router
from src.interface.users.users.follow_management.router import router as follow_router
from src.interface.posts.router import router as post_router
from src.interface.posts.likes.router import router as likes_router
from src.interface.posts.comments.router import router as comments_router
from src.interface.posts.reported_posts.router import router as report_post_router
from lib.fastapi.custom_middlewares import HandleExceptionMiddleware

disable_installed_extensions_check()

app = FastAPI(title="Social Media API")

app.add_middleware(HandleExceptionMiddleware)
app.include_router(auth_router)
app.include_router(base_user_router)
app.include_router(user_router)
app.include_router(follow_router)
app.include_router(post_router)
app.include_router(likes_router)
app.include_router(comments_router)
app.include_router(report_post_router)