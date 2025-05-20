from fastapi import APIRouter

from app.services.crawler import crawl_urls

router = APIRouter(prefix="/crawler", tags=["crawler"])


@router.get("", response_model=str)
async def start_crawler():
    return await crawl_urls()
