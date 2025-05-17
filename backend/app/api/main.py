from fastapi import APIRouter

from app.api.routes import (
    login,
    organizations,
    private,
    search_profiles,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(organizations.router)
api_router.include_router(search_profiles.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
