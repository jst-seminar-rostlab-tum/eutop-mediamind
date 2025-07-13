from datetime import datetime

from app.core.languages import Language
from app.core.logger import get_logger
from app.services.article_cleanup_service import ArticleCleanupService
from app.services.article_matching_service import ArticleMatchingService
from app.services.article_summary_service import ArticleSummaryService
from app.services.article_vector_service import ArticleVectorService
from app.services.email_service import EmailService
from app.services.report_service import ReportService
from app.services.translation_service import ArticleTranslationService
from app.services.web_harvester.crawler import CrawlerType
from app.services.web_harvester.web_harvester_orchestrator import (
    run_crawler,
    run_scraper,
)

logger = get_logger(__name__)


async def run(datetime_start: datetime, datetime_end: datetime):
    """Run a pipeline for the given date range."""
    logger.info(f"Running pipeline from {datetime_start} to {datetime_end}")

    logger.info("Running crawler and scraper")
    await run_crawler(
        CrawlerType.NewsAPICrawler,
        date_start=datetime_start,
        date_end=datetime_end,
    )
    await run_scraper()

    logger.info("Running Summarization and Entity Extraction")
    await ArticleSummaryService.run(
        datetime_start=datetime_start, datetime_end=datetime_end
    )

    logger.info("Running Translation")
    await ArticleTranslationService.run(
        datetime_start=datetime_start, datetime_end=datetime_end
    )

    logger.info("Running Embedding")
    vector_service = ArticleVectorService()
    await vector_service.index_summarized_articles_to_vector_store(
        datetime_start=datetime_start, datetime_end=datetime_end
    )

    logger.info("Running Article Matching")
    matching_service = ArticleMatchingService()
    await matching_service.run()

    logger.info("Report generation")
    # Returns the Report, presigned URL, dashboard URL and search profile
    reports_info = await ReportService.run(
        timeslot="morning", languages=[Language.EN, Language.DE]
    )
    logger.info(f"Generated {len(reports_info)} reports")

    logger.info("Sending emails")
    await EmailService.run(reports_info)

    logger.info("Cleaning up old articles (older than 180 days)")
    cleanup_service = ArticleCleanupService()
    cleanup_stats = await cleanup_service.cleanup_articles_older_than_days(
        days=180, batch_size=100, dry_run=False
    )
    logger.info(
        f"Article cleanup completed: "
        f"{cleanup_stats['articles_deleted']} articles deleted"
    )
