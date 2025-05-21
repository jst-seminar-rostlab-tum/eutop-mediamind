from bs4 import BeautifulSoup
from crawl4ai import *


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n").strip()


async def process_page(source_uris: list[str]):
    async with AsyncWebCrawler() as crawler:
        for source_uri in source_uris:
            result = await crawler.arun(
                url=source_uri,
            )
        print(result.markdown)
