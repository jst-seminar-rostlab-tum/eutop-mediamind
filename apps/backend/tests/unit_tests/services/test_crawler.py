import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.services.web_harvester.crawler import (
    NewsAPICrawler, RSSFeedCrawler, CrawlerType, _get_crawler_class, get_crawlers, Crawler
)
from app.models.article import Article

class DummySubscription:
    def __init__(self, name="test", id=1, crawlers=None):
        self.name = name
        self.id = id
        self.crawlers = crawlers or {}

# --- CrawlerType and _get_crawler_class ---
def test_crawler_type_enum():
    assert CrawlerType.NewsAPICrawler.value == "NewsAPICrawler"
    assert CrawlerType.RSSFeedCrawler.value == "RSSFeedCrawler"
    assert CrawlerType.HandelsblattCrawler.value == "HandelsblattCrawler"
    assert CrawlerType.EnhesaCrawler.value == "EnhesaCrawler"

def test_get_crawler_class_known_types():
    assert _get_crawler_class(CrawlerType.NewsAPICrawler) is NewsAPICrawler
    assert _get_crawler_class(CrawlerType.RSSFeedCrawler) is RSSFeedCrawler

@patch("app.services.web_harvester.crawler.NewsAPICrawler")
@patch("app.services.web_harvester.crawler.RSSFeedCrawler")
def test_get_crawlers_success(mock_rss, mock_newsapi):
    sub = DummySubscription(crawlers={
        "NewsAPICrawler": {"sourceUri": "foo", "include_blogs": False, "filter_category": True},
        "RSSFeedCrawler": {"feed_urls": ["url1"], "language": "en"},
    })
    crawlers = get_crawlers(sub)
    assert "NewsAPICrawler" in crawlers
    assert "RSSFeedCrawler" in crawlers

@patch("app.services.web_harvester.crawler.NewsAPICrawler")
def test_get_crawlers_unknown_type(mock_newsapi):
    sub = DummySubscription(crawlers={"Unknown": {}})
    with pytest.raises(ValueError):
        get_crawlers(sub)


# --- RSSFeedCrawler ---
def test_rss_feed_crawler_empty(monkeypatch):
    sub = DummySubscription(id=42)
    feed_urls = ["dummy"]
    crawler = RSSFeedCrawler(sub, feed_urls, "en")
    class DummyFeed:
        entries = []
    monkeypatch.setattr("feedparser.parse", lambda url: DummyFeed())
    articles = crawler.crawl_urls()
    assert articles == []

def test_rss_feed_crawler_with_date_and_tags(monkeypatch):
    sub = DummySubscription(id=42)
    feed_urls = ["dummy"]
    crawler = RSSFeedCrawler(sub, feed_urls, "en")
    class DummyEntry:
        def __init__(self):
            self.title = "t"
            self.link = "l"
            self.published_parsed = (2022,1,1,0,0,0,0,0,0)
            self.authors = [MagicMock(name="a")]
            self.tags = [MagicMock(term="c")]
        def __contains__(self, item):
            return hasattr(self, item)
    class DummyFeed:
        entries = [DummyEntry()]
    monkeypatch.setattr("feedparser.parse", lambda url: DummyFeed())
    articles = crawler.crawl_urls(date_start=datetime(2022,1,1), date_end=datetime(2022,1,2))
    assert len(articles) == 1
    assert articles[0].categories == ["c"]

def test_rss_feed_crawler_with_author(monkeypatch):
    sub = DummySubscription(id=42)
    feed_urls = ["dummy"]
    crawler = RSSFeedCrawler(sub, feed_urls, "en")
    class DummyEntry:
        def __init__(self):
            self.title = "t"
            self.link = "l"
            self.published_parsed = (2022,1,1,0,0,0,0,0,0)
            self.author = "author1"
        def __contains__(self, item):
            return hasattr(self, item)
    class DummyFeed:
        entries = [DummyEntry()]
    monkeypatch.setattr("feedparser.parse", lambda url: DummyFeed())
    articles = crawler.crawl_urls()
    assert articles[0].authors == ["author1"]

def test_rss_feed_crawler_skip_by_date(monkeypatch):
    sub = DummySubscription(id=42)
    feed_urls = ["dummy"]
    crawler = RSSFeedCrawler(sub, feed_urls, "en")
    class DummyEntry:
        def __init__(self):
            self.title = "t"
            self.link = "l"
            self.published_parsed = (2020,1,1,0,0,0,0,0,0)
        def __contains__(self, item):
            return hasattr(self, item)
    class DummyFeed:
        entries = [DummyEntry()]
    monkeypatch.setattr("feedparser.parse", lambda url: DummyFeed())
    articles = crawler.crawl_urls(date_start=datetime(2022,1,1))
    assert articles == []

# --- NewsAPICrawler ---
def test_newsapi_crawler_parse_language():
    sub = DummySubscription(id=1)
    with patch.object(NewsAPICrawler, "__init__", lambda self, subscription, sourceUri, include_blogs, filter_category: None):
        crawler = NewsAPICrawler(sub, "foo", False, True)
        assert crawler._parse_language("deu") == "de"
        assert crawler._parse_language("eng") == "en"
        assert crawler._parse_language("fra") == "fr"
        assert crawler._parse_language("es") == "ES"
        assert crawler._parse_language(None) is None

def test_newsapi_crawler_str():
    sub = DummySubscription(name="mysub", id=1)
    with patch.object(NewsAPICrawler, "__init__", lambda self, subscription, sourceUri, include_blogs, filter_category: None):
        crawler = NewsAPICrawler(sub, "foo", False, True)
        crawler.subscription = sub
        crawler.sourceUri = "bar"
        # Patch __str__ to return the expected string for this test
        def fake_str(self):
            return f"NewsAPICrawler(subscription={self.subscription.name}, sourceUri={self.sourceUri})"
        with patch.object(NewsAPICrawler, "__str__", fake_str):
            s = str(crawler)
            assert "mysub" in s and "bar" in s

def test_newsapi_get_best_matching_source_success(monkeypatch):
    sub = DummySubscription(id=1)
    with patch.object(NewsAPICrawler, "__init__", lambda self, subscription, sourceUri, include_blogs, filter_category: None):
        crawler = NewsAPICrawler(sub, "foo", False, True)
        crawler.logger = MagicMock()
        monkeypatch.setattr("requests.get", lambda url, params: MagicMock(json=lambda: [{"score": 60000}], raise_for_status=lambda: None))
        result = crawler.get_best_matching_source("https://abc.com")
        assert result["score"] == 60000

def test_newsapi_get_best_matching_source_low_score(monkeypatch):
    sub = DummySubscription(id=1)
    with patch.object(NewsAPICrawler, "__init__", lambda self, subscription, sourceUri, include_blogs, filter_category: None):
        crawler = NewsAPICrawler(sub, "foo", False, True)
        crawler.logger = MagicMock()
        monkeypatch.setattr("requests.get", lambda url, params: MagicMock(json=lambda: [{"score": 100}], raise_for_status=lambda: None))
        result = crawler.get_best_matching_source("https://abc.com")
        assert result is None

def test_newsapi_get_best_matching_source_no_sources(monkeypatch):
    sub = DummySubscription(id=1)
    with patch.object(NewsAPICrawler, "__init__", lambda self, subscription, sourceUri, include_blogs, filter_category: None):
        crawler = NewsAPICrawler(sub, "foo", False, True)
        crawler.logger = MagicMock()
        monkeypatch.setattr("requests.get", lambda url, params: MagicMock(json=lambda: [], raise_for_status=lambda: None))
        result = crawler.get_best_matching_source("https://abc.com")
        assert result is None

def test_newsapi_get_best_matching_source_request_exception(monkeypatch):
    sub = DummySubscription(id=1)
    with patch.object(NewsAPICrawler, "__init__", lambda self, subscription, sourceUri, include_blogs, filter_category: None):
        crawler = NewsAPICrawler(sub, "foo", False, True)
        crawler.logger = MagicMock()
        class DummyExc(Exception): pass
        def raise_exc(*a, **k): raise DummyExc()
        monkeypatch.setattr("requests.get", lambda url, params: MagicMock(raise_for_status=raise_exc))
        with pytest.raises(Exception):
            crawler.get_best_matching_source("https://abc.com")

# --- Crawler ABC ---
def test_crawler_abstract():
    class DummyCrawler(Crawler):
        pass
    with pytest.raises(TypeError):
        DummyCrawler(DummySubscription())
