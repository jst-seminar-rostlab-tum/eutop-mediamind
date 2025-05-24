import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlmodel import Field, Relationship, SQLModel
from starlette.middleware.cors import CORSMiddleware


from app.core.config import settings
from app.core.db import engine  # ensure database tables are created
from app.api.v1.routes import routers as v1_routers
from app.core.config import configs
from app.core.logger import get_logger

logger = get_logger(__name__)

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


logger.info("Starting FastAPI app initialization.")


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(
                dsn=settings.SENTRY_DSN,  # noqa: E501
                send_default_pii=True,
                traces_sample_rate=1.0,
                environment=configs.ENV,
            )
    

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    version="0.0.1"
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


SQLModel.metadata.create_all(engine)

app.include_router(api_router, prefix=settings.API_V1_STR)

logger.info("FastAPI app initialized successfully.")