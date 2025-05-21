from datetime import date, timedelta

from app.utils.crawl4ai import process_page
from app.utils.newsapi_ai import (
    get_articles_from_news_api_ai,
    get_breaking_events_from_news_api_ai,
)


async def crawl_and_scrape_urls():
    # two DB request for domains where "included_in_newsApi_ai" = true and where != true
    source_uris_with_news_api = [
        "bild.de",
        "faz.net",
        "plus.faz.net",
        "spiegel.de",
    ]  # later DB request
    source_uris_without_news_api = ["bild.de"]
    today = date.today()
    yesterday = today - timedelta(days=1)

    date_start = yesterday.strftime("%Y-%m-%d")
    date_end = today.strftime("%Y-%m-%d")
    try:
        articles = await get_articles_from_news_api_ai(
            source_uris_with_news_api, date_start, date_end
        )
        articles_2 = await process_page(source_uris_without_news_api)
    except Exception as e:
        print(e)
    # some checks maybe?
    # scrape articles_2 for meta_data
    # write them in the DB
    # Trigger scraping process


async def get_breaking_events():
    events = await get_breaking_events_from_news_api_ai()
    for event in events:
        print(event["summary"])
    return events
