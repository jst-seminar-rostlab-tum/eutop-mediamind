import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.routes import routers as v1_routers
from app.core.config import configs
from app.core.logger import get_logger


class AppCreator:
    logger = get_logger(__name__)

    def __init__(self):
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info  # noqa: E501
        if configs.SENTRY_DSN and configs.ENVIRONMENT != "local":
            sentry_sdk.init(
                dsn="https://b8eee5aa4743a1999a60a0ea24756735@o4509334816489472.ingest.de.sentry.io/4509334833135696",  # noqa: E501
                send_default_pii=True,
                traces_sample_rate=1.0,
                environment=configs.ENV,
            )

        self.logger.info("Starting FastAPI app initialization.")
        # set app default
        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            openapi_url="/api/openapi.json",
            docs_url="/api/docs",
            version="0.0.1",
        )

        # set cors
        if configs.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[
                    str(origin) for origin in configs.BACKEND_CORS_ORIGINS
                ],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        self.app.include_router(v1_routers, prefix="/api/v1")
        self.logger.info("FastAPI app initialized successfully.")


app_creator = AppCreator()
app = app_creator.app