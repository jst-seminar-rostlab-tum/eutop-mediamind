from firecrawl import FirecrawlApp, ScrapeOptions

app = FirecrawlApp(api_key="fc-cd85fb222f80404fb964f0523cd8f4d7")

# Scrape a website:


# Crawl a website:
def fire_crawl():
    crawl_status = app.crawl_url(
        "https://firecrawl.dev",
        limit=10,
        scrape_options=ScrapeOptions(formats=["markdown", "html"]),
    )
    print(crawl_status)
