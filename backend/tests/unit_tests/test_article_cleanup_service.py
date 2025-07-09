"""
Tests for Article Cleanup Service
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from app.services.article_cleanup_service import ArticleCleanupService
from app.models.article import Article, ArticleStatus


@pytest.fixture
def cleanup_service():
    """Create a cleanup service instance for testing."""
    with patch('app.services.article_cleanup_service.ArticleVectorService'):
        return ArticleCleanupService()


@pytest.fixture
def sample_articles():
    """Create sample articles for testing."""
    now = datetime.now()
    old_date = now - timedelta(days=200)
    recent_date = now - timedelta(days=50)
    
    old_articles = []
    for i in range(3):
        article = Article(
            id=uuid.uuid4(),
            title=f"Old Article {i}",
            content=f"Old content {i}",
            url=f"https://example.com/old/{i}",
            published_at=old_date,
            subscription_id=uuid.uuid4(),
            status=ArticleStatus.EMBEDDED
        )
        old_articles.append(article)
    
    recent_articles = []
    for i in range(2):
        article = Article(
            id=uuid.uuid4(),
            title=f"Recent Article {i}",
            content=f"Recent content {i}",
            url=f"https://example.com/recent/{i}",
            published_at=recent_date,
            subscription_id=uuid.uuid4(),
            status=ArticleStatus.EMBEDDED
        )
        recent_articles.append(article)
    
    return old_articles, recent_articles


class TestArticleCleanupService:
    """Test cases for ArticleCleanupService."""

    @pytest.mark.asyncio
    async def test_get_cleanup_preview(self, cleanup_service, sample_articles):
        """Test getting a preview of what would be cleaned up."""
        old_articles, recent_articles = sample_articles
        all_articles = old_articles + recent_articles
        
        with patch('app.services.article_cleanup_service.async_session') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # Mock the article query to return only old articles
            mock_execute = AsyncMock()
            mock_execute.scalars.return_value.all.return_value = old_articles
            mock_session_instance.execute.return_value = mock_execute
            
            preview = await cleanup_service.get_cleanup_preview(days=180)
            
            assert preview["articles_to_delete"] == 3
            assert "cutoff_date" in preview
            assert preview["entities_to_delete"] == 0  # No entities in mock
            assert preview["keyword_links_to_delete"] == 0  # No links in mock
            assert preview["matches_to_delete"] == 0  # No matches in mock

    @pytest.mark.asyncio
    async def test_cleanup_articles_dry_run(self, cleanup_service, sample_articles):
        """Test cleanup in dry run mode."""
        old_articles, recent_articles = sample_articles
        
        with patch('app.services.article_cleanup_service.async_session') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # Mock the count query
            mock_execute = AsyncMock()
            mock_execute.scalars.return_value.all.return_value = old_articles
            mock_session_instance.execute.return_value = mock_execute
            
            stats = await cleanup_service.cleanup_articles_older_than_days(
                days=180, batch_size=100, dry_run=True
            )
            
            assert stats["articles_processed"] == 3
            assert stats["articles_deleted"] == 0  # No actual deletion in dry run
            assert stats["errors"] == 0
            assert "cutoff_date" in stats

    @pytest.mark.asyncio
    async def test_process_article_batch_empty(self, cleanup_service):
        """Test processing an empty batch."""
        cutoff_date = datetime.now() - timedelta(days=180)
        
        with patch('app.services.article_cleanup_service.async_session') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # Mock empty result
            mock_execute = AsyncMock()
            mock_execute.scalars.return_value.all.return_value = []
            mock_session_instance.execute.return_value = mock_execute
            
            stats = await cleanup_service._process_article_batch(
                cutoff_date, batch_size=100, offset=0
            )
            
            assert stats["batch_size"] == 0
            assert stats["articles_deleted"] == 0

    @pytest.mark.asyncio
    async def test_delete_article_entities(self, cleanup_service):
        """Test deleting article entities."""
        article_ids = [uuid.uuid4(), uuid.uuid4()]
        
        mock_session = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.rowcount = 5
        mock_session.execute.return_value = mock_execute
        
        deleted_count = await cleanup_service._delete_article_entities(
            mock_session, article_ids
        )
        
        assert deleted_count == 5
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_article_keyword_links(self, cleanup_service):
        """Test deleting article keyword links."""
        article_ids = [uuid.uuid4(), uuid.uuid4()]
        
        mock_session = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.rowcount = 3
        mock_session.execute.return_value = mock_execute
        
        deleted_count = await cleanup_service._delete_article_keyword_links(
            mock_session, article_ids
        )
        
        assert deleted_count == 3
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_article_matches(self, cleanup_service):
        """Test deleting article matches."""
        article_ids = [uuid.uuid4(), uuid.uuid4()]
        
        mock_session = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.rowcount = 7
        mock_session.execute.return_value = mock_execute
        
        deleted_count = await cleanup_service._delete_article_matches(
            mock_session, article_ids
        )
        
        assert deleted_count == 7
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_from_vector_store(self, cleanup_service):
        """Test deleting articles from vector store."""
        article_ids = [uuid.uuid4(), uuid.uuid4()]
        
        # Mock the vector service delete method
        cleanup_service.vector_service.delete_articles_by_ids = MagicMock(return_value=2)
        
        deleted_count = await cleanup_service._delete_from_vector_store(article_ids)
        
        assert deleted_count == 2
        cleanup_service.vector_service.delete_articles_by_ids.assert_called_once_with(
            [str(aid) for aid in article_ids]
        )

    @pytest.mark.asyncio
    async def test_delete_articles(self, cleanup_service):
        """Test deleting the articles themselves."""
        article_ids = [uuid.uuid4(), uuid.uuid4()]
        
        mock_session = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.rowcount = 2
        mock_session.execute.return_value = mock_execute
        
        deleted_count = await cleanup_service._delete_articles(
            mock_session, article_ids
        )
        
        assert deleted_count == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_from_vector_store_error_handling(self, cleanup_service):
        """Test error handling when vector store deletion fails."""
        article_ids = [uuid.uuid4()]
        
        # Mock the vector service to raise an exception
        cleanup_service.vector_service.delete_articles_by_ids = MagicMock(
            side_effect=Exception("Vector store error")
        )
        
        deleted_count = await cleanup_service._delete_from_vector_store(article_ids)
        
        assert deleted_count == 0  # Should return 0 on error

    def test_empty_article_ids_handling(self, cleanup_service):
        """Test that methods handle empty article ID lists correctly."""
        import asyncio
        
        # All these methods should return 0 for empty lists
        async def test_empty():
            mock_session = AsyncMock()
            
            entities = await cleanup_service._delete_article_entities(mock_session, [])
            keywords = await cleanup_service._delete_article_keyword_links(mock_session, [])
            matches = await cleanup_service._delete_article_matches(mock_session, [])
            articles = await cleanup_service._delete_articles(mock_session, [])
            vectors = await cleanup_service._delete_from_vector_store([])
            
            assert entities == 0
            assert keywords == 0
            assert matches == 0
            assert articles == 0
            assert vectors == 0
        
        asyncio.run(test_empty())
