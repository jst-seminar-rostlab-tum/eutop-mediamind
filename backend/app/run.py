import asyncio

from sqlmodel import Session

from alembic import command
from alembic.config import Config
from app.core.db import engine, init_db
from app.main import app_creator


# Start background tasks here if needed
@app_creator.app.on_event("startup")
async def startup_event():
    run_migrations()
    asyncio.create_task(init_session())


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def init_session():
    with Session(engine) as session:
        await init_db(session)
