import asyncio
from datetime import datetime

from app.core.logger import get_logger
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


async def run(date_start: datetime, date_end: datetime, language: str = "en"):
    """Run a pipeline for the given date range."""
    # print(f"Started Pi: {span_start}, Span end: {span_end}")
    logger.info(f"Running pipeline from {date_start} to {date_end}")

    logger.info("Running crawler and scraper")
    await run_crawler(
        CrawlerType.NewsAPICrawler, date_start=date_start, date_end=date_end
    )
    await run_scraper()

    logger.info("Running Summarization and Entity Extraction")
    await ArticleSummaryService.run(date_start=date_start, date_end=date_end)

    logger.info("Running Translation")
    await ArticleTranslationService.run(
        date_start=date_start, date_end=date_end
    )

    logger.info("Running Embedding")
    vector_service = ArticleVectorService()
    await vector_service.index_summarized_articles_to_vector_store(
        date_start=date_start, date_end=date_end
    )

    logger.info("Running Article Matching")
    matching_service = ArticleMatchingService()
    await matching_service.run()

    logger.info("Report generation")
    # returns the Report, presigned URL, dashboard URL and search profile
    reports_info = await ReportService.run(
        timeslot="morning", language=language
    )
    logger.info(f"Generated {len(reports_info)} reports")

    logger.info("Sending emails")
    await EmailService.run(reports_info)


if __name__ == "__main__":
    # Example usage
    start_date = datetime(2025, 6, 30)
    end_date = datetime.now()
    asyncio.run(run(date_start=start_date, date_end=end_date))
