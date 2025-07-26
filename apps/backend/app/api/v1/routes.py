from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.chatbot_controller import router as chatbot_router
from app.api.v1.endpoints.crawler_controller import router as crawler_router
from app.api.v1.endpoints.jobs_controller import router as job_router
from app.api.v1.endpoints.organization_controller import (
    router as organization_router,
)
from app.api.v1.endpoints.report_controller import router as report_router
from app.api.v1.endpoints.search_profile_controller import (
    router as search_profile_router,
)
from app.api.v1.endpoints.subscription_controller import (
    router as subscription_router,
)
from app.api.v1.endpoints.user_controller import router as user_router

routers = APIRouter()
router_list = [
    user_router,
    search_profile_router,
    subscription_router,
    job_router,
    crawler_router,
    report_router,
    chatbot_router,
    organization_router,
]


@routers.get("/healthcheck", tags=["healthcheck"])
async def healthcheck():
    return JSONResponse(content={"status": "ok"})


for router in router_list:
    routers.include_router(router)
