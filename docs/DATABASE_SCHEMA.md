# Database Schema Documentation

## Overview

The MediaMind system uses a PostgreSQL database with tables supporting news article processing, user management, matching algorithms, and reporting functionality.

## Database Tables & File Locations

### Backend Tables (`apps/backend/app/models/`)

- **article.py** - News articles with multilingual support
- **user.py** - User management
- **organization.py** - Organization structure
- **search_profile.py** - Content filtering profiles
- **subscription.py** - News sources configuration
- **match.py** - Article-profile matching results
- **topic.py** - Thematic content groupings
- **keyword.py** - Search and matching keywords
- **entity.py** - Named entity extraction results
- **report.py** - Generated PDF report metadata (S3 key references, not the actual PDF files)
- **email.py** - Email delivery tracking
- **email_conversation.py** - Chatbot conversation threads
- **matching_run.py** - Algorithm execution tracking
- **breaking_news.py** - Breaking news notifications
- **associations.py** - Many-to-many relationship tables
