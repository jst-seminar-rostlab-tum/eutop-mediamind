from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.article_controller import router as article_router
from app.api.v1.endpoints.email_controller import router as email_router
from app.api.v1.endpoints.keyword_controller import router as keyword_router
from app.api.v1.endpoints.match_controller import router as match_router
from app.api.v1.endpoints.report_controller import router as report_router
from app.api.v1.endpoints.search_profile_controller import (
    router as search_profile_router,
)
from app.api.v1.endpoints.subscription_controller import (
    router as subscription_router,
)
from app.api.v1.endpoints.topic_controller import router as topic_router
from app.api.v1.endpoints.user_controller import router as user_router
from app.api.v1.endpoints.vector_store_controller import (
    router as vector_store_router,
)

routers = APIRouter()
router_list = [
    user_router,
    search_profile_router,
    subscription_router,
    email_router,
    vector_store_router,
    article_router,
    topic_router,
    keyword_router,
    match_router,
    report_router,
]


@routers.get("/healthcheck", tags=["healthcheck"])
async def healthcheck():
    return JSONResponse(content={"status": "ok"})


for router in router_list:
    routers.include_router(router)
