from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.auth_controller import router as auth_router
from app.api.v1.endpoints.search_profile_controller import (
    router as search_profile_router,
)
from app.api.v1.endpoints.user_controller import router as user_router

routers = APIRouter()
router_list = [user_router, auth_router, search_profile_router]


@routers.get("/healthcheck", tags=["healthcheck"])
async def healthcheck():
    return JSONResponse(content={"status": "ok"})


for router in router_list:
    routers.include_router(router)
