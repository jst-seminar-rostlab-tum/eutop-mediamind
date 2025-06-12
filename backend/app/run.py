import asyncio

from sqlmodel import Session

from app.core.db import init_db
from app.main import app_creator


# Start background tasks here if needed
@app_creator.app.on_event("startup")
async def startup_event():
    asyncio.create_task(init_db())
