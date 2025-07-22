import pytest
from unittest.mock import MagicMock, patch
from app.services.web_harvester.web_harvester_orchestrator import (
    _scraper_error_handling, _handle_login_if_needed, _scrape_articles, run_selenium_code
)
from app.models.article import Article, ArticleStatus
from app.models.subscription import Subscription

class DummyScraper:
    def __init__(self):
        self.logger = MagicMock()
    def extract(self, html, article):
        article.content = "scraped content"
        article.status = ArticleStatus.SCRAPED
        return article

def test_scraper_error_handling_sets_error():
    articles = [Article(id=1), Article(id=2)]
    error = "Some error"
    result = _scraper_error_handling(articles, error)
    for article in result:
        assert article.status == ArticleStatus.ERROR
        assert article.note == error

def test_handle_login_if_needed_paywall_success():
    subscription = MagicMock(name="test")
    subscription.paywall = True
    scraper = DummyScraper()
    driver = MagicMock()
    wait = MagicMock()
    with patch('app.services.web_harvester.utils.web_utils.hardcoded_login', return_value=True):
        assert _handle_login_if_needed(subscription, scraper, driver, wait) is True

def test_handle_login_if_needed_paywall_fail():
    subscription = MagicMock(name="test")
    subscription.paywall = True
    scraper = DummyScraper()
    driver = MagicMock()
    wait = MagicMock()
    # Patch the path as imported in the orchestrator, not where it's defined
    with patch('app.services.web_harvester.web_harvester_orchestrator.hardcoded_login', return_value=False):
        assert _handle_login_if_needed(subscription, scraper, driver, wait) is False

def test_handle_login_if_needed_no_paywall():
    subscription = MagicMock(name="test")
    subscription.paywall = False
    scraper = DummyScraper()
    driver = MagicMock()
    wait = MagicMock()
    assert _handle_login_if_needed(subscription, scraper, driver, wait) is True

def test_scrape_articles_success():
    scraper = DummyScraper()
    driver = MagicMock()
    articles = [Article(id=1, url="http://a.com"), Article(id=2, url="http://b.com")]
    with patch('app.services.web_harvester.web_harvester_orchestrator.safe_page_load', return_value=True), \
         patch('app.services.web_harvester.web_harvester_orchestrator.get_response_code', return_value=200), \
         patch('app.services.web_harvester.web_harvester_orchestrator.safe_execute_script', return_value="complete"):
        result = _scrape_articles(scraper, driver, articles)
        assert all(a.status == ArticleStatus.SCRAPED for a in result)
        assert all(a.content == "scraped content" for a in result)

def test_scrape_articles_load_fail():
    scraper = DummyScraper()
    driver = MagicMock()
    articles = [Article(id=1, url="http://a.com")]
    with patch('app.services.web_harvester.web_harvester_orchestrator.safe_page_load', return_value=False):
        result = _scrape_articles(scraper, driver, articles)
        assert result[0].status == ArticleStatus.ERROR
        assert "Failed to load page" in result[0].note


# 100% coverage for run_selenium_code and _handle_logout_and_cleanup
import types
from app.services.web_harvester.web_harvester_orchestrator import run_selenium_code, _handle_logout_and_cleanup

class DummySubscription:
    def __init__(self, paywall=True, llm_login_attempt=None):
        self.paywall = paywall
        self.llm_login_attempt = llm_login_attempt
        self.name = "test"
        self.scrapers = DummyScraper()
        self.logger = MagicMock()
        self.domain = "http://a.com"


def test_run_selenium_code_login_fail_llm_update_fail(monkeypatch):
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    subscription = DummySubscription(paywall=True, llm_login_attempt=now - timedelta(days=8))
    articles = [Article(id=1, url="http://a.com")]
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator._handle_login_if_needed', lambda *a, **k: False)
    class DummyFuture:
        def result(self):
            return None
    monkeypatch.setattr('asyncio.run_coroutine_threadsafe', lambda *a, **k: DummyFuture())
    from unittest.mock import MagicMock
    result = run_selenium_code(articles, subscription, subscription.scrapers, MagicMock())
    assert result[0].status == ArticleStatus.ERROR
    assert "Login failed" in result[0].note

def test_run_selenium_code_login_fail_llm_update_success_but_still_fail(monkeypatch):
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    subscription = DummySubscription(paywall=True, llm_login_attempt=now - timedelta(days=8))
    articles = [Article(id=1, url="http://a.com")]
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator._handle_login_if_needed', lambda *a, **k: False)
    class DummyFuture:
        def result(self):
            return subscription
    monkeypatch.setattr('asyncio.run_coroutine_threadsafe', lambda *a, **k: DummyFuture())
    from unittest.mock import MagicMock
    result = run_selenium_code(articles, subscription, subscription.scrapers, MagicMock())
    assert result[0].status == ArticleStatus.ERROR
    assert "Login failed" in result[0].note

def test_run_selenium_code_scraper_raises(monkeypatch):
    subscription = DummySubscription(paywall=False)
    articles = [Article(id=1, url="http://a.com")]
    class BadScraper(DummyScraper):
        def extract(self, html, article):
            raise Exception("extract failed")
    def fake_handle_login(*a, **k): return True
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator._handle_login_if_needed', fake_handle_login)
    def fake_create_driver(*a, **k):
        driver = MagicMock()
        driver.page_source = "<html></html>"
        wait = MagicMock()
        return driver, wait
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.create_driver', fake_create_driver)
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.safe_page_load', lambda *a, **k: True)
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.get_response_code', lambda *a, **k: 200)
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.safe_execute_script', lambda *a, **k: "complete")
    subscription.scrapers = BadScraper()
    from unittest.mock import MagicMock
    result = run_selenium_code(articles, subscription, subscription.scrapers, MagicMock())
    assert result[0].status == ArticleStatus.ERROR
    assert "extract failed" in result[0].note

def test_run_selenium_code_finally(monkeypatch):
    subscription = DummySubscription(paywall=True)
    articles = [Article(id=1, url="http://a.com")]
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator._handle_login_if_needed', lambda *a, **k: True)
    class DummyDriver:
        def quit(self):
            DummyDriver.quit_called = True
    DummyDriver.quit_called = False
    def fake_create_driver(*a, **k):
        return DummyDriver(), MagicMock()
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.create_driver', fake_create_driver)
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.safe_page_load', lambda *a, **k: True)
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.get_response_code', lambda *a, **k: 200)
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.safe_execute_script', lambda *a, **k: "complete")
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.hardcoded_logout', lambda *a, **k: None)
    from unittest.mock import MagicMock
    result = run_selenium_code(articles, subscription, subscription.scrapers, MagicMock())
    assert DummyDriver.quit_called

def test_handle_logout_and_cleanup_all_paths(monkeypatch):
    # paywall True, login_success True, logout ok
    driver = MagicMock()
    wait = MagicMock()
    subscription = DummySubscription(paywall=True)
    scraper = MagicMock()
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.hardcoded_logout', lambda **kwargs: None)
    driver.quit = MagicMock()
    _handle_logout_and_cleanup(driver, wait, subscription, scraper, True)
    driver.quit.assert_called_once()

def test_handle_logout_and_cleanup_logout_raises(monkeypatch):
    driver = MagicMock()
    wait = MagicMock()
    subscription = DummySubscription(paywall=True)
    scraper = MagicMock()
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.hardcoded_logout', lambda **kwargs: (_ for _ in ()).throw(Exception("logout error")))
    driver.quit = MagicMock()
    _handle_logout_and_cleanup(driver, wait, subscription, scraper, True)
    driver.quit.assert_called_once()

def test_handle_logout_and_cleanup_quit_raises(monkeypatch):
    driver = MagicMock()
    wait = MagicMock()
    subscription = DummySubscription(paywall=True)
    scraper = MagicMock()
    monkeypatch.setattr('app.services.web_harvester.web_harvester_orchestrator.hardcoded_logout', lambda **kwargs: None)
    def bad_quit(): raise Exception("quit error")
    driver.quit = bad_quit
    # Should not raise
    _handle_logout_and_cleanup(driver, wait, subscription, scraper, True)
