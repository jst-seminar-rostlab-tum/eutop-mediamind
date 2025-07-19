# ArticleCleanupService Documentation

## Overview

The `ArticleCleanupService` is a critical maintenance component responsible for database hygiene and storage cost management. It performs comprehensive cleanup of articles older than a specified retention period while maintaining referential integrity.

## Core Functionality

### Main Method: `cleanup_articles_older_than_days()`

**Purpose**: Deletes articles older than specified days along with all related data.

**Parameters**:

- `days` (default: 180): Number of days to look back for article deletion
- `batch_size` (default: 100): Number of articles to process per batch

**Returns**: Dictionary with cleanup statistics

### Five-Phase Deletion Process (in order):

The service implements a sophisticated cascade deletion system to ensure referential integrity:

1. **Article Entities Cleanup** - Deletes `ArticleEntity` (persons, orgs, events)
2. **Keyword Links Cleanup** - Removes `ArticleKeywordLink` (keeps keywords)
3. **Matches Cleanup** - Delete `Match` relations to search profiles
4. **Vector Store Cleanup** - Removes article embeddings from Qdrant
5. **Article Deletion** - Deltes `Article` records

## Integration Points

- **Pipeline Integration**: Executed in main processing pipeline after email sending
- **Vector Store**: Uses `ArticleVectorService` for Qdrant operations
- **Database**: Operates on PostgreSQL with foreign key constraints

## Usage Examples

### Custom Retention Period

```python
service = ArticleCleanupService()
stats = await service.cleanup_articles_older_than_days(days=90, batch_size=50)
```

## Important Notes

⚠️ **Critical Operation**:
Irreversible deletion. Test thoroughly, ensure backups, monitor resources.

## File Locations

- **Service**: `apps/backend/app/services/article_cleanup_service.py`
- **Vector Integration**: `apps/backend/app/services/article_vector_service.py`
- **Pipeline Integration**: `apps/backend/app/services/pipeline.py`
- **Models**: `apps/backend/app/models` (article.py, entity.py, match.py, associations.py)
