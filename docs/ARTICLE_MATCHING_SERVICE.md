# ArticleMatchingService Documentation

## Overview

The `ArticleMatchingService` performs intelligent matching between articles and search profiles using a three-phase algorithm that combines vector similarity search with keyword matching.

**Location:** `apps/backend/app/services/article_matching_service.py`

## Algorithm

### Three-Phase Matching Process

#### Phase 1: Topic Matching

- Combines topic name with all keywords into search queries
- Uses vector similarity search against article database
- **Threshold:** 0.7
- **Output:** `topic_id → {article_id: topic_score}`

#### Phase 2: Keyword Matching

- Searches each keyword individually against articles from Phase 1
- **Threshold:** 0.1
- **Output:** `topic_id → article_id → keyword_id → [scores]`

#### Phase 3: Score Combination

- Combines topic and keyword scores with weighted average
- **Weights:** Topic: 0.7, Keyword: 0.3
- Deduplicates articles (one match per article)
- Sorts by combined score (descending)

### Configuration

```python
weights = {"topic": 0.7, "keyword": 0.3}
topic_score_threshold = 0.7
keyword_score_threshold = 0.1
```

## Key Methods

### Batch Processing

```python
async def run(batch_size=100)
```

Processes all search profiles in parallel batches.

## Data Models

- **Match:** Stores article-profile matches with scores
- **MatchingRun:** Tracks algorithm versions and execution runs
- **SearchProfile:** Contains topics and keywords for matching

## Integration

### Dependencies

- `ArticleVectorService` - Vector similarity search
- `MatchRepository` - Data persistence
- `SearchProfileRepository` - Profile data access

## Configuration Tuning

### Thresholds

- **Increase topic threshold (0.7)** → Fewer, higher-quality topic matches
- **Increase keyword threshold (0.1)** → Fewer, higher-quality keyword matches

### Weights

- **Increase topic weight (0.7)** → Favor topic-level similarity
- **Increase keyword weight (0.3)** → Favor individual keyword matches
