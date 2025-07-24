# Scraping

The scraping process takes all articles with a 'NEW' status for each subscription. If the newspaper website is paywalled, the login must be completed before scraping (see [LOGIN_SCRAPING.md](LOGIN_SCRAPING.md)).

The scraping process works like this:
1. The page's html is extracted using selenium
2. The html is passed to the scraper for content and metadata extraction
3. After the scraping is completed, the extracted content is added to its respective article in the database
4. The article's status is set to 'SCRAPED' if the process succeeded, otherwise it is set to 'ERROR'

The following scrapers are available in the system:

### 1. TrafilaturaScraper

This scraper uses the trafilatura library to extract the content and metadata. It is configured per subscription in the database using the following structure:

```json
{
    "TrafilaturaScraper": {
        "trafilatura_kwargs": {
            "prune_xpath": <xpath_expression>, // Removes matching elements before parsing
            "author_blacklist": ["<string>", "..."] // Removes matching author names

        }
    }
}
```

These "trafilatura_kwargs" config is optional and can be used to fine-tune the extraction, it should only be included if the scraper is not extracting content correctly. In most cases, the following minimal configuration is sufficient:

```json
{"TrafilaturaScraper": {}}
```

The scraper also includes a hardcoded default configuration that ensures consistent and high-quality results. This should not be modified, as it has proven effective:

```json
default_trafilatura_kwargs = {
    "output_format": "markdown",
    "include_tables": False,
    "prune_xpath": "//h1 | //title",
    "include_comments": False,
}
```

### 2. Newspaper4kScraper

This scraper uses the Newspaper4k python library for content and metadata extraction. Just like the Trafilatura scraper, it is defined as a json per subscription:

```json
{
    "Newspaper4kScraper": {
        "newspaper_kwargs": {
            "language": <string_language_code>, // set article's language for parsing
            "memoize_articles": <boolean>, // disables article caching
            "fetch_images": <boolean> // controls whether images should be downloaded
        }
    }
}
```

If no newspaper_kwargs are specified, the scraper uses these default settings defined in the code:

```json
{
  "language": "en",
  "memoize_articles": false,
  "fetch_images": true
}
```
