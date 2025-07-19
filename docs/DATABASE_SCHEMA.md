# Database Schema Documentation

## Overview

The MediaMind system uses a PostgreSQL database with 18+ tables supporting news article processing, user management, matching algorithms, and reporting functionality.

## Database Tables & File Locations

### Backend Tables (`apps/backend/app/models/`)

- **articles.py** - News articles with multilingual support
- **users.py** - User management and authentication
- **organizations.py** - Multi-tenant organization structure
- **search_profiles.py** - Content filtering profiles
- **subscriptions.py** - News sources configuration
- **matches.py** - Article-profile matching results
- **topics.py** - Thematic content groupings
- **keywords.py** - Search and matching keywords
- **entities.py** - Named entity extraction results
- **reports.py** - Generated PDF reports
- **emails.py** - Email delivery tracking
- **email_conversations.py** - Chatbot conversation threads
- **chat_messages.py** - Individual chat interactions
- **matching_runs.py** - Algorithm execution tracking
- **crawl_stats.py** - Web crawling performance metrics

### API Tables (`apps/api/app/models/`)

- **associations.py** - Many-to-many relationship tables

## Database Schema Diagram

```mermaid
erDiagram
    organizations ||--o{ users : "has"
    organizations ||--o{ search_profiles : "owns"
    organizations }o--o{ subscriptions : "accesses"

    users ||--o{ search_profiles : "creates"
    users }o--o{ search_profiles : "permissions"

    search_profiles ||--o{ topics : "contains"
    search_profiles ||--o{ matches : "generates"
    search_profiles }o--o{ subscriptions : "filters"

    subscriptions ||--o{ articles : "publishes"
    subscriptions ||--o{ crawl_stats : "tracks"

    articles ||--o{ matches : "matched_in"
    articles ||--o{ entities : "contains"
    articles }o--o{ keywords : "tagged_with"

    topics ||--o{ matches : "categorizes"
    topics }o--o{ keywords : "defined_by"

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
        string role
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
        json scrapers
    }

    articles {
        uuid id PK
        string title
        text content
        string url
        timestamp published_at
        string language
        string status
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
```

## Key Relationships

### Core Data Flow

1. **Organizations** contain **Users** and own **Search Profiles**
2. **Subscriptions** publish **Articles** that get crawled and processed
3. **Search Profiles** define filtering criteria and generate **Topics**
4. **Articles** are matched against **Topics** to create **Matches**
5. **Matching Runs** execute algorithms and generate **Reports**
6. **Reports** are distributed via **Emails**

### Content Processing Pipeline

- Articles are crawled from Subscriptions
- Named Entities and Keywords are extracted from Articles
- Matching algorithms connect Articles to Search Profiles via Topics
- Results are compiled into Reports and sent as Emails

### User & Permission Model

- Organizations provide multi-tenant data isolation
- Users have role-based access (admin > maintainer > member)
- Search Profiles support hierarchical permissions (owner > editor > reader)

## Migration Files

- **Backend**: `apps/backend/alembic/versions/`
- **API**: `apps/api/alembic/versions/`
- **Configuration**: `alembic.ini` in respective app directories

## Technical Notes

- All tables use UUID primary keys
- Multilingual support (EN/DE) throughout the system
- JSON fields for flexible configuration storage
- Encrypted credentials for secure data handling
