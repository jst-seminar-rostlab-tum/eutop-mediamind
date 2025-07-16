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

## Technical Implementation

### Batch Processing

- Processes articles in configurable batches (default: 100)
- Uses offset-based pagination for memory efficiency
- Provides transaction safety with automatic rollback on errors

### Statistics Tracking

The service tracks comprehensive statistics:

```python
{
    "articles_processed": 0,
    "articles_deleted": 0,
    "entities_deleted": 0,
    "keyword_links_deleted": 0,
    "matches_deleted": 0,
    "vector_store_deletions": 0,
    "errors": 0,
    "cutoff_date": "2024-01-16T17:00:00"
}
```

### Error Handling

- Database transaction rollback on batch failures
- Graceful error logging with detailed statistics
- Continues processing on non-critical errors
- Vector store deletion errors are logged but don't stop the process

## Configuration

### Default Settings

- **Retention Period**: 180 days
- **Batch Size**: 100 articles
- **Cutoff Calculation**: `datetime.now() - timedelta(days=days)`

### Integration Points

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

## Performance Considerations

### Scalability

- Batch processing prevents memory overload
- Query optimization through index usage on `published_at`
- Configurable batch size for different system loads

### Resource Usage

- Memory efficient through streaming approach
- Database connection pooling through SQLAlchemy
- Minimal vector store API calls through batch operations

## Safety Procedures

### Monitoring During Cleanup

- Monitor batch processing statistics
- Track error rates and types
- Verify deletion counts align with expectations

### Post-Cleanup Validation

- Verify referential integrity maintenance
- Check vector store consistency
- Validate cleanup statistics accuracy

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

### Pipeline Integration

Located in `apps/api/app/services/pipeline.py` (lines 64-70):

```python
# Article cleanup (180 days retention, 100 article batches)
cleanup_service = ArticleCleanupService()
cleanup_stats = await cleanup_service.cleanup_articles_older_than_days()
```

## Troubleshooting

### Common Issues

1. **Vector Store Connection Errors**: Check Qdrant availability and credentials
2. **Database Lock Timeouts**: Reduce batch size during high-traffic periods
3. **Memory Issues**: Lower batch size for large article volumes

## Important Notes

⚠️ **Critical Operation**: This service performs irreversible data deletion. Always:

- Test in non-production environments first
- Ensure proper backups before execution
- Monitor system resources during cleanup
- Verify cleanup statistics after completion

🔒 **Security**: The service requires database write permissions and vector store access. Ensure proper authentication and authorization.

📊 **Monitoring**: Integrate cleanup statistics into monitoring systems to track storage optimization and identify potential issues.

## File Locations

- **Service**: `apps/api/app/services/article_cleanup_service.py`
- **Vector Integration**: `apps/api/app/services/article_vector_service.py`
- **Pipeline Integration**: `apps/api/app/services/pipeline.py`
- **Models**: `apps/api/app/models/` (article.py, entity.py, match.py, associations.py)
