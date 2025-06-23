from app.services.article_matching_service import ArticleMatchingService
from app.core.logger import get_logger
from app.services.article_vector_service import ArticleVectorService

logger = get_logger(__name__)


def get_article_matching_service() -> ArticleMatchingService:
    """
    Dependency to get the ArticleMatchingService instance.
    """
    return ArticleMatchingService()


def get_article_vector_service() -> ArticleVectorService:
    """
    Returns a instance of ArticleVectorService.

    Raises:
        RuntimeError: If the service initialization fails.
    """
    try:
        return ArticleVectorService()
    except Exception as e:
        logger.error(f"Failed to get vector service: {str(e)}")
        raise RuntimeError(f"Failed to get vector service: {str(e)}")
