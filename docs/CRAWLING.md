# Crawling

Crawlers can be categorized as follows:

### 1. NewsAPICrawler

This crawler uses NewsAPI to fetch articles. It is configured using a JSON structure:

```json
{
    "NewsAPICrawler": {
        "filter_category": <boolean>,
        "include_blogs": <boolean>,
        "sourceUri": <newspaper_domain>
    }
}
```

### 2. RSSFeedCrawler

This crawler retrieves article links from RSS feeds. Its configuration is also defined in JSON:

```json
{
    "RSSFeedCrawler": {
        "feed_urls": <list_of_RSS_feed_links>,
        "language": <language_code>
    }
}
```

The crawler configuration JSON must be stored in the database for each active subscription.

After crawling, articles are inserted into the database without their content, and their status is set to `NEW`.

### 3. Custom Crawlers

For newspapers that are not supported by NewsAPI, do not provide RSS feeds, or where the login and scraping process does not work as expected, the following custom crawler types are defined:

- `HandelsblattCrawler`
- `EnhesaCrawler`
- `EuramsCrawler`

Every custom crawler is defined for a specific domain, and based on crawl4ai. These custom crawlersc can handle login, crawling, and scraping. Since the website structures are suitable, no additional data cleaning is required. After processing, articles are stored directly in the database with the status `SCRAPED`, as the scraping step is already integrated.
