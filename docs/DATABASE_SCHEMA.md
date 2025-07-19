# Database Schema Documentation

## Overview

The MediaMind system uses a PostgreSQL database with 18+ tables supporting news article processing, user management, matching algorithms, and reporting functionality.

## Database Tables & File Locations

### Backend Tables (`apps/backend/app/models/`)

- **article.py** - News articles with multilingual support
- **user.py** - User management and authentication
- **organization.py** - Multi-tenant organization structure
- **search_profile.py** - Content filtering profiles
- **subscription.py** - News sources configuration
- **match.py** - Article-profile matching results
- **topic.py** - Thematic content groupings
- **keyword.py** - Search and matching keywords
- **entity.py** - Named entity extraction results
- **report.py** - Generated PDF reports
- **email.py** - Email delivery tracking
- **email_conversation.py** - Chatbot conversation threads
- **chat_message.py** - Individual chat interactions
- **matching_run.py** - Algorithm execution tracking
- **crawl_stats.py** - Web crawling performance metrics
- **auth.py** - Authentication models and utilities
- **breaking_news.py** - Breaking news notifications
- **associations.py** - Many-to-many relationship tables

## Database Schema Diagram

```mermaid
erDiagram
    organizations ||--o{ users : "has"
    organizations ||--o{ search_profiles : "owns"
    organizations }o--o{ subscriptions : "accesses via organizations_subscriptions"

    users }o--o{ search_profiles : "permissions via users_search_profiles"

    search_profiles ||--o{ topics : "contains"
    search_profiles ||--o{ matches : "generates"
    search_profiles }o--o{ subscriptions : "filters via search_profiles_subscriptions"

    subscriptions ||--o{ articles : "publishes"
    subscriptions ||--o{ crawl_stats : "tracks"

    articles ||--o{ matches : "matched_in"
    articles ||--o{ entities : "contains"
    articles }o--o{ keywords : "tagged_with via articles_keywords"

    topics ||--o{ matches : "categorizes"
    topics }o--o{ keywords : "defined_by via topics_keywords"

    matching_runs ||--o{ matches : "executes"
    matching_runs ||--o{ reports : "generates"

    search_profiles ||--o{ reports : "produces"
    reports ||--o{ emails : "sent_as"

    email_conversations ||--o{ chat_messages : "contains"

    organizations {
        uuid id PK
        string name
        string email
        string vault_path
        boolean pdf_as_link
    }

    users {
        uuid id PK
        string clerk_id
        string email
        string first_name
        string last_name
        boolean is_superuser
        boolean breaking_news
        string language
        string role
        string gender
        uuid organization_id FK
    }

    search_profiles {
        uuid id PK
        string name
        boolean is_public
        uuid created_by_id FK
        uuid owner_id FK
        uuid organization_id FK
        string language
    }

    subscriptions {
        uuid id PK
        string name
        string domain
        boolean paywall
        boolean is_active
        json crawlers
        json login_config
        json scrapers
        bytea encrypted_secrets
        bytea encrypted_username
    }

    articles {
        uuid id PK
        string title
        text content
        string url
        string image_url
        json authors
        timestamp published_at
        string language
        json categories
        text summary
        string status
        integer relevance
        text title_en
        text title_de
        text content_en
        text content_de
        text summary_en
        text summary_de
        timestamp crawled_at
        timestamp scraped_at
        text note
        uuid subscription_id FK
    }

    topics {
        uuid id PK
        string name
        text description
        uuid search_profile_id FK
    }

    matches {
        uuid id PK
        uuid article_id FK
        uuid search_profile_id FK
        uuid topic_id FK
        integer sorting_order
        text comment
        float score
        timestamp matched_at
        uuid matching_run_id FK
    }

    keywords {
        uuid id PK
        string keyword
        string language
    }

    entities {
        uuid id PK
        string entity_name
        string entity_type
        uuid article_id FK
    }

    reports {
        uuid id PK
        string file_path
        uuid search_profile_id FK
        uuid matching_run_id FK
    }

    emails {
        uuid id PK
        string email_type
        string status
        uuid report_id FK
    }

    matching_runs {
        uuid id PK
        timestamp started_at
        timestamp completed_at
        string status
    }

    crawl_stats {
        uuid id PK
        integer articles_found
        timestamp crawl_date
        uuid subscription_id FK
    }

    email_conversations {
        uuid id PK
        string title
        string status
    }

    chat_messages {
        uuid id PK
        text content
        string sender_type
        uuid conversation_id FK
    }

    %% Association Tables
    organizations_subscriptions {
        uuid organization_id PK,FK
        uuid subscription_id PK,FK
    }

    users_search_profiles {
        uuid user_id PK,FK
        uuid search_profile_id PK,FK
    }

    search_profiles_subscriptions {
        uuid search_profile_id PK,FK
        uuid subscription_id PK,FK
    }

    articles_keywords {
        uuid article_id PK,FK
        uuid keyword_id PK,FK
        float score
    }

    topics_keywords {
        uuid topic_id PK,FK
        uuid keyword_id PK,FK
    }
```

## Migration Files

- **Backend**: `apps/backend/alembic/versions/`
- **API**: `apps/api/alembic/versions/`
- **Configuration**: `alembic.ini` in respective app directories

## Technical Notes

- All tables use UUID primary keys
- Multilingual support (EN/DE) throughout the system
- Encrypted credentials for secure data handling
