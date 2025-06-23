from app.core.logger import get_logger
from app.services.article_matching_service import ArticleMatchingService
from app.services.article_vector_service import ArticleVectorService

logger = get_logger(__name__)


def get_article_matching_service() -> ArticleMatchingService:
    """
    Dependency to get the ArticleMatchingService instance.
    """
    try:
        return ArticleMatchingService()
    except Exception as e:
        logger.error(f"Failed to get article " f" service: {str(e)}")
        raise RuntimeError(
            f"Failed to get article " f"matching service: {str(e)}"
        )


def get_article_vector_service() -> ArticleVectorService:
    """
    Dependency to get the ArticleVectorService instance.

    Raises:
        RuntimeError: If the service initialization fails.
    """
    try:
        return ArticleVectorService()
    except Exception as e:
        logger.error(f"Failed to get vector service: {str(e)}")
        raise RuntimeError(f"Failed to get vector service: {str(e)}")
