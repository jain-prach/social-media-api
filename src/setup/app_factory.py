from fastapi import FastAPI

from src.interface.users.router import router as base_user_router
from lib.fastapi.custom_middlewares import HandleExceptionMiddleware

app = FastAPI(title="Social Media API")

app.add_middleware(HandleExceptionMiddleware)
app.include_router(base_user_router)