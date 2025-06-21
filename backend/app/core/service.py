from app.services.article_matching_service import ArticleMatchingService


def get_article_matching_service() -> ArticleMatchingService:
    """
    Dependency to get the ArticleMatchingService instance.
    """
    return ArticleMatchingService()
