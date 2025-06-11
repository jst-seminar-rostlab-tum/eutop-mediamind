import asyncio

import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.routes import routers as v1_routers
from app.core.config import configs
from app.core.logger import get_logger
from app.initial_data import main


class AppCreator:
    logger = get_logger(__name__)

    def __init__(self):
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info  # noqa: E501
        if configs.SENTRY_DSN and configs.ENVIRONMENT != "local":
            sentry_sdk.init(
                dsn=configs.SENTRY_DSN,  # noqa: E501
                send_default_pii=True,
                traces_sample_rate=1.0,
                environment=configs.ENVIRONMENT,
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
                allow_origins=configs.all_cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        self.app.include_router(v1_routers, prefix="/api/v1")
        asyncio.create_task(main())
        self.logger.info("FastAPI app initialized successfully.")


app_creator = AppCreator()
app = app_creator.app
