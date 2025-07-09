from fastapi.routing import APIRouter
from app.core.logger import get_logger
from datetime import datetime, date
from app.services import pipeline
import asyncio

from app.services.email_service import EmailService



router = APIRouter(prefix="/jobs", tags=["jobs"])

logger = get_logger(__name__)

@router.get("/email")
async def email_job():
    """
    This endpoint is a placeholder for an email job.
    It currently does nothing but can be extended to send emails.
    """
    await EmailService.send_scheduled_emails()

@router.get("/pipeline")
async def trigger_pipeline():
    datetime_start: datetime = datetime.combine(date.today(), datetime.min.time())
    datetime_end: datetime = datetime.now()

    logger.info(f"Triggering pipeline from {datetime_start} to {datetime_end}")
    asyncio.create_task(
        pipeline.run(
            datetime_start=datetime_start,
            datetime_end=datetime_end,
        )
    )

