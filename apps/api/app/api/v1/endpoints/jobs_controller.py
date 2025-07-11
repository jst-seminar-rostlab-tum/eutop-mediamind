import asyncio

from fastapi.routing import APIRouter

from app.core.logger import get_logger
from app.schemas.job_schemas import JobResponse, JobStatus, PipelineJobRequest
from app.services import pipeline
from app.services.email_service import EmailService

router = APIRouter(prefix="/jobs", tags=["jobs"])

logger = get_logger(__name__)


@router.post("/email")
async def email_job() -> JobResponse:
    try:
        await EmailService.send_scheduled_emails()
    except Exception as e:
        return JobResponse(
            JobStatus.FAILED,
            message=f"Failed to send scheduled emails: {str(e)}",
        )
    return JobResponse(
        JobStatus.COMPLETED,
        message="Email job has been completed successfully.",
    )


@router.post("/pipeline")
async def trigger_pipeline(
    req: PipelineJobRequest = PipelineJobRequest(),
) -> JobResponse:
    logger.info(f"Triggering pipeline from {req.start} to {req.end}")
    try:
        asyncio.create_task(
            pipeline.run(
                datetime_start=req.start,
                datetime_end=req.end,
            )
        )
    except Exception as e:
        return JobResponse(
            JobStatus.FAILED, message=f"Failed to trigger pipeline: {str(e)}"
        )

    return JobResponse(
        JobStatus.COMPLETED,
        message="Pipeline job has been triggered successfully.",
    )
