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

### Five-Phase Deletion Process

The service implements a sophisticated cascade deletion system to ensure referential integrity:

1. **Article Entities Cleanup** - Removes `ArticleEntity` records (persons, organizations, events)
2. **Keyword Links Cleanup** - Removes `ArticleKeywordLink` associations while preserving keywords
3. **Matches Cleanup** - Removes `Match` records linking articles to search profiles
4. **Vector Store Cleanup** - Removes article embeddings from Qdrant vector database
5. **Article Deletion** - Final removal of article records

## Integration Points

- **Pipeline Integration**: Executed in main processing pipeline after email sending
- **Vector Store**: Uses `ArticleVectorService` for Qdrant operations
- **Database**: Operates on PostgreSQL with foreign key constraints

## Database Schema Impact

### Affected Tables

- `articles` - Primary entities being cleaned
- `article_entities` - Named entities extracted from articles
- `article_keyword_links` - Article-keyword associations with scores
- `matches` - Article-search profile matching results

### Deletion Order

The specific deletion order ensures referential integrity:

1. Child entities first (entities, keyword links, matches)
2. Vector store embeddings
3. Parent articles last

## Usage Examples

### Standard Cleanup (180 days)

```python
service = ArticleCleanupService()
stats = await service.cleanup_articles_older_than_days()
```

### Custom Retention Period

```python
service = ArticleCleanupService()
stats = await service.cleanup_articles_older_than_days(days=90, batch_size=50)
```

## Important Notes

⚠️ **Critical Operation**: This service performs irreversible data deletion. Always:

- Test in non-production environments first
- Ensure proper backups before execution
- Monitor system resources during cleanup
- Verify cleanup statistics after completion

## File Locations

- **Service**: `apps/api/app/services/article_cleanup_service.py`
- **Vector Integration**: `apps/api/app/services/article_vector_service.py`
- **Pipeline Integration**: `apps/api/app/services/pipeline.py`
- **Models**: `apps/api/app/models/` (article.py, entity.py, match.py, associations.py)
