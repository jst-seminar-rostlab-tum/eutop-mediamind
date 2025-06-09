import asyncio

from app.initial_data import main as init_data_main
from app.main import app_creator


# Start background tasks here if needed
@app_creator.app.on_event("startup")
async def startup_event():
    asyncio.create_task(init_data_main())
