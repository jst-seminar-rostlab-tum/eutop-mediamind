from fastapi import APIRouter

from app.services.crawler import crawl_and_scrape_urls, get_breaking_events

router = APIRouter(prefix="/crawler", tags=["crawler"])


@router.get("/get_articles", response_model=str)
async def start_crawling_and_scraping():
    return await crawl_and_scrape_urls()


@router.get("/get_breaking/events", response_model=list[dict])
async def start_get_breaking_events():
    return await get_breaking_events()
