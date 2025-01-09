from fastapi import FastAPI

from src.interface.auth.router import router as auth_router
from src.interface.users.router import router as base_user_router
from src.interface.users.users.router import router as user_router
from lib.fastapi.custom_middlewares import HandleExceptionMiddleware

app = FastAPI(title="Social Media API")

app.add_middleware(HandleExceptionMiddleware)
app.include_router(auth_router)
app.include_router(base_user_router)
app.include_router(user_router)