from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.search_profile_controller import (
    router as search_profile_router,
)
from app.api.v1.endpoints.user_controller import router as user_router
from app.api.v1.endpoints.email_controller import router as email_router

routers = APIRouter()
router_list = [user_router, search_profile_router, email_router]


@routers.get("/healthcheck", tags=["healthcheck"])
async def healthcheck():
    return JSONResponse(content={"status": "ok"})


for router in router_list:
    routers.include_router(router)
