# ArticleMatchingService Documentation

## Overview

The `ArticleMatchingService` intelligently matches articles to search profiles using a hybrid approach that combines semantic vector similarity with keyword matching for optimal precision and recall.

**Location:** `apps/backend/app/services/article_matching_service.py`

## Uses ArticleVectorService

- Dense vector: uses OpenAI embeddings with cosine similarity search
- Sparse vector: uses BM25

You can tune the retrieval in `apps/backend/app/services/article_vector_service.py`

## Algorithm

### Three-Phase Matching Process

#### Phase 1: Topic Matching

- Merges topic names with keywords to create comprehensive search queries
- Performs vector similarity search against the article database
- **Threshold:** 0.7 (high precision)
- **Output:** `topic_id → {article_id: topic_score}`

#### Phase 2: Keyword Matching

- Executes individual keyword searches on articles from Phase 1
- **Threshold:** 0.1 (high recall)
- **Output:** `topic_id → article_id → keyword_id → [scores]`

#### Phase 3: Score Combination

- Applies weighted average to merge topic and keyword scores
- **Weights:** Topic: 0.7 (semantic relevance), Keyword: 0.3 (specific terms)
- Removes duplicate articles and ranks by combined score (highest first)

### Configuration

```python
weights = {"topic": 0.7, "keyword": 0.3}
topic_score_threshold = 0.7
keyword_score_threshold = 0.1
```

## Implementation

### Core Method

```python
async def run(batch_size=100)
```

Executes the complete matching pipeline with configurable batch processing for memory efficiency and parallel execution.

## Configuration Tuning

### Threshold Optimization

- **Topic threshold ↑ (0.7)** → Higher precision, fewer matches
- **Keyword threshold ↑ (0.1)** → More selective keyword matching

### Weight Balancing

- **Topic weight ↑ (0.7)** → Emphasize semantic similarity
- **Keyword weight ↑ (0.3)** → Emphasize exact term matches
