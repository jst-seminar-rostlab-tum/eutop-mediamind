# Crawling

Each active subscription must have a crawler assigned, either via configuration json or as a custom crawler. Crawlers can be categorized as follows:

### 1. NewsAPICrawler

This crawler uses NewsAPI to fetch articles from supported news domains. It is configured using the following JSON structure:

```json
{
    "NewsAPICrawler": {
        "filter_category": <boolean>, // Apply default category filters
        "include_blogs": <boolean>, // Include blog sources in results
        "sourceUri": <newspaper_domain>
    }
}
```

When assigning this crawler to a subscription in the database, make sure to include the "sourceUri" field in the configuration. This field is **mandatory**, omitting it will result in an error during crawler initialization.. The rest of the fields in the configuration are optional.

In order for this crawler to work, a valid NewsAPI API key must be defined in the system configuration.

After crawling, articles are stored in the database (without content), and their status is set to `NEW`.

### 2. RSSFeedCrawler

This crawler uses newspaper RSS feeds to extract articles. It is configured using the following structure:

```json
{
    "RSSFeedCrawler": {
        "feed_urls": <list_of_RSS_feed_links>,
        "language": <language_code>
    }
}
```

Both "feed_urls" and "language" are **required** fields, omitting either will result in an error during crawler initialization. For each feed URL provided, the crawler uses the `feedparser` library to parse and extract entries. After crawling, articles are stored in the database (without content), and their status is set to `NEW`.

### 3. Custom Crawlers

For newspapers that are not supported by NewsAPI, do not provide RSS feeds, or where the login and scraping process does not work as expected, the following custom crawler types are defined:

- `HandelsblattCrawler`
- `EnhesaCrawler`
- `EuramsCrawler`

Every custom crawler is defined for a specific domain, and based on crawl4ai. These custom crawlers can handle login, crawling, and scraping. Since the website structures are suitable, no additional data cleaning is required. After processing, articles are stored directly in the database with the status `SCRAPED`, as the scraping step is already integrated.
