# Pipeline Services Overview

This document provides a high-level overview of all services executed in the MediaMind pipeline for future developers maintaining and extending the system.

## Pipeline Execution Order

The main pipeline is orchestrated in `apps/backend/app/services/pipeline.py` and executes the following services in sequence:

### 1. Data Collection Services

#### Web Harvester Services (run_crawler & run_scraper)
**Location:** `apps/backend/app/services/web_harvester/`

**Purpose:** Collect news articles from various sources and extract their full content.

**Components:**
- **Crawlers** (`crawler.py`): Discover article URLs from news sources
  - `NewsAPICrawler`: Uses EventRegistry API to find articles from specific news sources
  - `RSSFeedCrawler`: Crawls RSS feeds for article URLs. This should be triggered on a regular basis by the scheduler. 
  - `FtCrawler`, `HandelsblattCrawler`, `EnhesaCrawler`: Specialized crawlers for paywall sites. These have special mechanism to avoid botting.
- **Scrapers** (`scraper.py`): Extract full article content from URLs
  - `TrafilaturaScraper`: Primary content extraction using Trafilatura library
  - `Newspaper4kScraper`: Scraper using Newspaper4k library

In the data/subscription.json file it is specified which crawlers and scrapers are enabled for each subscription. One Subscription can have multiple crawlers but only one scraper. To further extend these classes one can add new classes and simply register them in the registry variable in the `crawler.py` and `scraper.py`, update the subscription.json and start the data seeding to update the database.

**Functionality:**
- Handles paywall authentication for premium sources
- Stores articles with metadata (title, content, authors, published date, etc.)
- Implements rate limiting and error handling

### 2. Content Cleaning Services

#### Article Cleaner
**Location:** `apps/backend/app/services/article_cleaner/`

**Purpose:** Clean and validate scraped article content to ensure quality and consistency.

**Execution:** Runs automatically within the `run_scraper()` function after content extraction.

**Functionality:**
- **Content Cleaning**: Removes formatting artifacts, markdown symbols, author lines, metadata, and duplicate content
- **Character Validation**: Ensures articles contain only allowed characters and removes problematic encoding
- **URL Detection**: Identifies and flags content with embedded URLs or path references
- **Minimum Content Check**: Validates articles meet minimum length requirements (150+ characters)


### 3. Content Processing Services

#### ArticleSummaryService
**Location:** `apps/backend/app/services/article_summary_service.py`

**Purpose:** Generate concise summaries and extract entities from news articles using LLM.

**Functionality:**
- Creates structured summaries of article content
- Extracts entities: people, organizations, industries, events, citations
- Utilizes LLMs to generate the output

#### ArticleTranslationService
**Location:** `apps/backend/app/services/translation_service.py`

**Purpose:** Translate articles and entities to multiple languages for international accessibility.

**Functionality:**
- Translates article titles, summaries, and content to target languages (EN, DE)
- Handles entity translation (person names, organization names, etc.)
- Language detection to avoid unnecessary translations

### 4. Search & Indexing Services

#### ArticleVectorService
**Location:** `apps/backend/app/services/article_vector_service.py`

**Purpose:** Create semantic embeddings and index articles in vector database for similarity search.

**Functionality:**
- Converts article summaries into vector embeddings
- Stores vectors in Qdrant vector database
- Enables semantic similarity search across articles
- Supports collection management (create, delete, list)
- Batch indexing for performance

**Use Case:** Powers the article matching system for finding relevant content

#### ArticleMatchingService
**Location:** `apps/backend/app/services/article_matching_service.py`

**Purpose:** Match articles to user search profiles based on topics and keywords.

**Algorithm:**
1. **Phase 1**: Vector similarity search against search profile topics
2. **Phase 2**: Keyword scoring using exact and fuzzy matching
3. **Phase 3**: Combined scoring and deduplication

**Scoring:**
- Topic relevance: 70% weight
- Keyword relevance: 30% weight
- Configurable thresholds for quality control

**Output:** Ranked matches between articles and search profiles

### 5. Report Generation & Distribution Services

#### ReportService
**Location:** `apps/backend/app/services/report_service.py`

**Purpose:** Generates PDF reports for search profiles.

**Features:**
- Creates reports based on newly matched articles in the run
- Generates one report per search profile and language
- Stores reports in AWS S3 with presigned URLs
- Handles empty reports when no matching articles found

#### PDFService
**Location:** `apps/backend/app/services/pdf_service/`

**Purpose:** Generate formatted PDF reports from matched articles.

**Components:**
- **Cover Page**: Title, date, reading time estimate, table of contents
- **Summary Section**: 3-column layout with article summaries and quick links
- **Full Articles**: Complete article content with metadata and entity information
- **Original Articles**: Appendix with untranslated content

**Functionality:**
- Multi-language support with dynamic content translation
- Professional styling with custom fonts and colors
- Rich metadata display (reading time, entities, keywords)
- Interactive elements (links, navigation anchors)
- Image inclusion from article URLs

#### EmailService
**Location:** `apps/backend/app/services/email_service.py`

**Purpose:** Send email notifications with PDF reports to subscribers.

**Functionality:**
- Personalizes emails based on user language preferences
- Supports PDF as attachment or download link (configurable)
- Multi-language email templates (EN, DE)
- Handles empty reports with appropriate messaging
- Email scheduling

## Key Technologies

- **LLM Integration**: LiteLLM API with OpenAI credentials for summarization and translation
- **Vector Database**: Qdrant for semantic search capabilities
- **PDF Generation**: ReportLab for document creation
- **Web Scraping**: Trafilatura, Newspaper4k, Crawl4AI, Selenium for content extraction
- **Async Processing**: Python asyncio for concurrent operations
- **Cloud Storage**: AWS S3 for report storage and distribution
