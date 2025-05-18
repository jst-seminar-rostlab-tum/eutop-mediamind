import asyncio
from crawl4ai.async_webcrawler import AsyncWebCrawler

class SimpleSpider(AsyncWebCrawler):
    name = "simple_spider"

    async def parse(self, response):
        # response.soup is a BeautifulSoup object
        title = response.soup.title.string if response.soup.title else ""
        paragraphs = [p.text.strip() for p in response.soup.find_all('p')]
        yield {
            "url": response.url,
            "title": title,
            "paragraphs": paragraphs
        }

if __name__ == "__main__":
    urls = [
        "https://www.python.org",
        "https://www.github.com"
    ]
    spider = SimpleSpider()
    async def main():
        for url in urls:
            await spider.arun(url)
    asyncio.run(main()) 