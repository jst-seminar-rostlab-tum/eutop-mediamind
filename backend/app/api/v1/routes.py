from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.article import router as article_router
from app.api.v1.endpoints.crawler_endpoint import router as crawler_router
from app.api.v1.endpoints.user import router as user_router

routers = APIRouter()
router_list = [user_router, crawler_router, article_router]


@routers.get("/healthcheck", tags=["healthcheck"])
async def healthcheck():
    return JSONResponse(content={"status": "ok"})


for router in router_list:
    routers.include_router(router)
