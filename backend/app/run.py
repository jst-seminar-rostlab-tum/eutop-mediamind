import asyncio

from sqlmodel import Session

from app.core.db import engine, init_db
from app.main import app_creator


# Start background tasks here if needed
@app_creator.app.on_event("startup")
async def startup_event():
    asyncio.create_task(init_session())


async def init_session():
    with Session(engine) as session:
        await init_db(session)
