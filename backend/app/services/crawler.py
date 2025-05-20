# from app.utils.firecrawl import crawl_status
import asyncio

from app.utils.crawl4ai import process_page
from app.utils.newsapi_ai import getarticles


async def crawl_urls():
    getarticles()
    asyncio.run(process_page())
