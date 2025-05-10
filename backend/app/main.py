from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.routes import routers as v1_routers
from app.core.config import configs


class AppCreator:
    def __init__(self):
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


app_creator = AppCreator()
app = app_creator.app
