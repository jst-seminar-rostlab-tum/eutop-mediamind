from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.user import router as user_router

routers = APIRouter()
router_list = [user_router, auth_router]


@routers.get("/healthcheck", tags=["healthcheck"])
async def healthcheck():
    return JSONResponse(content={"status": "ok"})


for router in router_list:
    routers.include_router(router)
