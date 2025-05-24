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
                dsn=configs.SENTRY_DSN,  # noqa: E501
                send_default_pii=True,
                traces_sample_rate=1.0,
                environment=configs.ENV,
            )

        self.logger.info("Starting FastAPI app initialization.")

        # Set app default
        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            openapi_url="/api/openapi.json",
            docs_url="/api/docs",
            generate_unique_id_function=self.custom_generate_unique_id,
            version="0.0.1",
        )

        # Set CORS middleware
        if configs.all_cors_origins:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=configs.all_cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # SQLModel.metadata.create_all(engine)

        # Include API routers
        self.app.include_router(v1_routers, prefix=configs.API_V1_STR)

        self.logger.info("FastAPI app initialized successfully.")

    def custom_generate_unique_id(self, route):
        return f"{route.tags[0]}-{route.name}"


app_creator = AppCreator()
app = app_creator.app
