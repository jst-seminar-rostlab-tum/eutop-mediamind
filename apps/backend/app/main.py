import sentry_sdk
from fastapi import FastAPI, Request
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.v1.routes import routers as v1_routers
from app.core.config import get_configs
from app.core.logger import get_logger

configs = get_configs()
logger = get_logger(__name__)


class AppCreator:
    def __init__(self):
        # Initialize Sentry for production
        if configs.SENTRY_DSN and configs.ENVIRONMENT != "local":
            sentry_sdk.init(
                dsn=configs.SENTRY_DSN,
                send_default_pii=True,
                traces_sample_rate=1.0,
                environment=configs.ENVIRONMENT,
            )

        logger.info("Starting FastAPI app initialization.")

        # Dynamically set servers based on .env/configs
        servers = configs.API_SERVERS
        if not servers:
            servers = [
                {
                    "url": "http://localhost:8000",
                    "description": "Local",
                },
            ]

        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            openapi_url="/api/v1/openapi.json",
            docs_url="/api/docs",
            version="0.0.1",
            servers=servers,
            swagger_ui_parameters={
                "tagsSorter": "alpha",
                "operationsSorter": "alpha",
            },
        )

        self._register_exception_handlers()
        self._configure_cors()
        self._include_routes()

        logger.info("FastAPI app initialized successfully.")

    def _register_exception_handlers(self):
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            logger.exception(f"Unhandled Exception: {exc} {request}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )

        @self.app.exception_handler(SQLAlchemyError)
        async def sqlalchemy_exception_handler(
            request: Request, exc: SQLAlchemyError
        ):
            logger.error(f"Database error: {exc} {request}")
            return JSONResponse(
                status_code=500,
                content={"detail": "A database error occurred."},
            )

    def _configure_cors(self):
        if configs.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=configs.all_cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def _include_routes(self):
        self.app.include_router(v1_routers, prefix="/api/v1")


# App exposure for Uvicorn
app_creator = AppCreator()
app = app_creator.app
