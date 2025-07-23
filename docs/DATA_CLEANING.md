


# Data Cleaning Overview

Data cleaning is a crucial step in the Eutop MediaMind content pipeline, ensuring that only high-quality, relevant, and well-formatted articles are stored and used for downstream tasks such as search, recommendation, and analytics.

**Objectives:**
- Remove noise, formatting artifacts, and irrelevant or low-quality content from freshly scraped articles.
- Ensure that stored articles meet quality standards for length, character set, and usefulness.
- Automate the cleaning process as much as possible, leveraging both local validation and LLM-based polishing.

**Pipeline Stages & Key Files:**
1. **Initial Scraping:**
   - Raw articles are collected from various sources by web crawlers.
   - (See: `app/services/web_harvester/`)
2. **Stage 1: Local Validation & Filtering**  
   - Quickly filter out articles with obvious issues (e.g., invalid characters, too short, etc.).
   - If the article passes, it is stored directly; if not, it proceeds to the next stage.
   - **Relevant file:** `app/services/article_cleaner/article_valid_check.py`
3. **Stage 2: LLM-based Polishing**  
   - Articles flagged in stage 1 are sent to an LLM, which attempts to clean, polish, and extract meaningful content.
   - If the LLM determines the article is still not useful, it may return an empty string. In this case, the article is given ERROR status and a note: `Article doesn't look like a news article after cleaning`.
   - **Relevant file:** `app/services/article_cleaner/cleaner_llm.py`  
   - **Orchestration:** See `app/services/web_harvester_orchestrator/` for how these stages are coordinated.
4. **Final Validation:**
   - Cleaned articles are validated again to ensure they meet all requirements before being stored in the database.
   - **Relevant file:** `app/services/article_cleaner/article_valid_check.py`

**Integration Points:**
- The cleaning logic is used in the ingestion pipeline, before articles are indexed or exposed to users.
- Validation functions are also used in unit/integration tests to ensure robustness against edge cases and noisy data.

**Core Usage:**

- Use `is_article_valid(text)` to check if cleaned content is valid (no illegal chars, no URLs, enough length).  
  (See: `app/services/article_cleaner/article_valid_check.py`)
- Use `ArticleCleaner().clean_plain_text(text)` to clean raw article content using LLMs (removes noise, formatting, and irrelevant parts).  
  (See: `app/services/article_cleaner/cleaner_llm.py`)
- Only valid, cleaned articles are stored in the database.

**Example:**
```python
raw_text = ...  # Raw news content
result = raw_text
if not is_article_valid(raw_text):
    result = ArticleCleaner().clean_plain_text(raw_text)
return result
```

For more details, see `apps/backend/app/services/article_cleaner/`.
