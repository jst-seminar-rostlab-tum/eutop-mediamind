import asyncio
import os
import json
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, BrowserConfig
from crawl4ai import CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv

load_dotenv()


class Newspaper(BaseModel):
    login_xpath: str


async def main():

    llm_extraction_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(provider="openai/gpt-4o-mini", 
                             api_token=os.getenv('OPENAI_API_KEY')),
        schema=Newspaper.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extract the xpath of the login element, whether it is a button, "
            "link, or other. The xpath must be made to work with selenium"
        ),
        chunk_token_threshold=1200,
        overlap_rate=0.1,
        apply_chunking=True,
        input_format="html",
        extra_args={"temperature": 0.1, "max_tokens": 1000},
        verbose=True
    )

    browser_config = BrowserConfig(
        verbose=True,
        headless=True,
        viewport_width=1280,
        viewport_height=720
    )

    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_extraction_strategy,
        cache_mode=CacheMode.BYPASS,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://epaper.handelsblatt.com/", config=crawl_config)

        if result.success:
            data = json.loads(result.extracted_content)
            print("Extracted items:", data)
        else:
            print("Error:", result.error_message)


asyncio.run(main())
