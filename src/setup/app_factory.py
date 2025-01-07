from fastapi import FastAPI

from src.interface.users.router import router as base_user_router

app = FastAPI(title="Social Media API")

app.include_router(base_user_router)