

class ArticleMatchingService:
    """Service for matching articles"""

    async def fetch_all_search_profiles(self, limit: int, offset: int):
        """
        Fetch all search profiles with pagination.
        """
