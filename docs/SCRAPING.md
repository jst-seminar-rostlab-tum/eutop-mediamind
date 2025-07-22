# Scraping

The scraping process takes all the articles with NEW status per subscription. Scraping is done with selenium. If the newspaper is paywalled, the login must be completed first (see [LOGIN_SCRAPING.md](LOGIN_SCRAPING.md)).

The page's html is extracted directly with selenium, which is then sent to one of the following scrapers:

* TrafilaturaScraper: uses the trafilatura library, and it is defined as a json with the following structure
```json
{
    "TrafilaturaScraper": {
        "trafilatura_kwargs": {
            <configuration>
        }
    }
}
```
This scraper extracts both content and metadata. In the code the scraper has the following deafault config:
```json
default_trafilatura_kwargs = {
    "output_format": "markdown",
    "include_tables": False,
    "prune_xpath": "//h1 | //title",
    "include_comments": False,
}
```
* Newspaper4kScraper: uses the Newspaper4k python library for content and metadata extraction. Just like the Trafilatura scraper, it is defined as a json
```json
{
    "Newspaper4kScraper": {
        "newspaper_kwargs": {
            <configuration>
        }
    }
}
```
Scrapers must be stored in the database for all active subscriptions.

After the scraping is completed, articles are set to SCRAPED status if the process succeeded, otherwise they'll be set to ERROR.