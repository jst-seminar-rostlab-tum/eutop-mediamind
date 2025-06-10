import asyncio
import json
import os
from datetime import date, timedelta

import pandas as pd

from app.services.scraper import process_urls
from app.utils.newsapi_ai import (
    get_articles_from_news_api_ai,
    get_breaking_events_from_news_api_ai,
)


async def crawl_and_scrape_urls():
    # two DB request for domains where "included_in_newsApi_ai" = true and where != true
    source_uris_with_news_api = [
        "product.enhesa.com/news-insight",
        "ft.com",
        "handelsblatt.com",
        "wiwo.de",
        "politico.eu",
        "heise.de",
    ]  # later DB request
    source_uris_without_news_api = ["bild.de"]
    today = date.today()
    yesterday = today - timedelta(days=1)

    date_start = yesterday.strftime("%Y-%m-%d")
    date_end = today.strftime("%Y-%m-%d")
    try:
        # articles = await get_articles_from_news_api_ai(
        #     source_uris_with_news_api, date_start, date_end
        # )
        # urls = [a["url"] for a in articles if "url" in a]
        # with open("test_urls.json", "w", encoding="utf-8") as f:
        #     json.dump(urls, f, ensure_ascii=False, indent=2)
        # print(f"✅ 已保存 {len(urls)} 个 URL 到 test_urls.json")

        with open(
            "backend/app/services/test_urls.json", "r", encoding="utf-8"
        ) as f:
            urls = json.load(f)
        results_from_crawl4ai = await process_urls(urls)

        # 保存为 Excel
        rows = []
        markdown_dir = "scraped_markdowns"
        os.makedirs(markdown_dir, exist_ok=True)

        for i, result in enumerate(results_from_crawl4ai):
            url = result.get("url", "")
            markdown = result.get("markdown", "")

            # 保存 markdown 到文件
            if markdown:
                filename = f"{markdown_dir}/article_{i+1}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(markdown)
            else:
                filename = ""

            # 添加到 dataframe
            rows.append(
                {
                    "url": url,
                    "markdown": markdown,
                }
            )

        # 存 Excel
        df = pd.DataFrame(rows)
        df.to_excel("scraped_articles.xlsx", index=False)
        print("✅ 抓取结果已保存到 scraped_articles.xlsx 和 markdown 文件夹中")

        # articles_2 = await process_page(source_uris_without_news_api)
    except Exception as e:
        print(e)
    # some checks maybe?
    # scrape articles_2 for meta_data
    # write them in the DB
    # Trigger scraping process


async def get_breaking_events():
    events = await get_breaking_events_from_news_api_ai()
    # for event in events:
    #     print(event["summary"])
    return events


if __name__ == "__main__":
    asyncio.run(crawl_and_scrape_urls())
