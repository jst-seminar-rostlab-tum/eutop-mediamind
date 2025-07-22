# Crawling

Crawlers can be of the following types:

* NewsAPICrawler: uses NewsAPI to obtain the articles. It is defined as a json with the following structure:
```json
{
    "NewsAPICrawler": {
        "filter_category": <boolean>,
        "include_blogs": <boolean>, 
        "sourceUri": <newspaper_domain>
    }
}
```
* RSSFeedCrawler: this type of crawler uses RSS feeds to obtain the articles' links. It is defined as a json as well:
```json
{
    "RSSFeedCrawler": {
        "feed_urls": <strings_list_with_RSS_feed_links>, 
        "language": <language_code>
    }
}
```
The json defining the crawler must be stored for each active subscription in the database.

For newspapers not supported by NewsAPI and without RSS feeds we define the following custom crawler types:
* FtCrawler
* HandelsblattCrawler
* EnhesaCrawler

After the crawling is finished, the articles are inserted in the database, without their content and with their status set to NEW.