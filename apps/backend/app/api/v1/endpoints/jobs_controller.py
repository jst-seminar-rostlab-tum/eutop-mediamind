import asyncio

from fastapi.routing import APIRouter

from app.core.logger import get_logger
from app.schemas.job_schemas import (
    JobResponse,
    JobStatus,
    PipelineJobRequest,
    RSSJobRequest,
)
from app.services import pipeline
from app.services.email_service import EmailService
from app.services.web_harvester.breaking_news_crawler import (
    fetch_breaking_news_newsapi,
)
from app.services.web_harvester.crawler import CrawlerType
from app.services.web_harvester.web_harvester_orchestrator import run_crawler

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
    logger.info(
        f"Triggering pipeline from {req.start} to {req.end} for"
        f" {req.time_period}"
    )
    try:
        asyncio.create_task(
            pipeline.run(
                datetime_start=req.start,
                datetime_end=req.end,
                time_period=req.time_period,
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


@router.post("/rss")
async def trigger_rss_crawling(
    req: RSSJobRequest = RSSJobRequest(),
) -> JobResponse:
    logger.info(f"Triggering RSS crawling from {req.start} to {req.end}")
    try:
        asyncio.create_task(
            run_crawler(
                CrawlerType.RSSFeedCrawler,
                date_start=req.start,
                date_end=req.end,
                limit=-1,
            )
        )
    except Exception as e:
        return JobResponse(
            JobStatus.FAILED,
            message=f"Failed to trigger RSS crawling: {str(e)}",
        )

    return JobResponse(
        JobStatus.COMPLETED,
        message="RSS crawling job has been triggered successfully.",
    )


@router.post("/breaking-news")
async def trigger_newsapi_crawling() -> JobResponse:
    logger.info("Triggering breaking news crawling")

    try:
        breaking_news = await fetch_breaking_news_newsapi()
    except Exception as e:
        return JobResponse(
            JobStatus.FAILED,
            message=f"Failed to trigger breaking news crawling: {str(e)}",
        )

    return JobResponse(
        JobStatus.COMPLETED,
        message=f"Crawled {len(breaking_news)} breaking news articles",
    )
