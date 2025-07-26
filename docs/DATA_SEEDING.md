# Data Seeding Guide

This guide explains how to seed the EUTOP MediaMind backend with initial data for subscriptions and credentials.

## Overview

The data seeding system loads initial data into the database to configure newspaper subscriptions and their associated login credentials. The seeding process handles two main data types:

1. **Subscriptions** - Configuration for newspaper sources including domains, paywalls, and scraping settings
2. **Credentials** - Login credentials for subscription-based newspaper access

## Required Files

### 1. Subscriptions Data (Required)

**File:** `apps/backend/data/subscriptions.json`

This file contains the configuration for all newspaper subscriptions and must be present for the application to work properly.

**Format:**
```json
[
  {
    "name": "Newspaper Name",
    "domain": "https://newspaper.com",
    "paywall": true,
    "is_active": true,
    "login_config": {
      "cookies_button": "//button[contains(@class, 'cookie-accept')]",
      "login_button": "//a[@id='login-link']",
      "user_input": "//input[@id='username']",
      "password_input": "//input[@type='password']",
      "submit_button": "//button[@type='submit']"
    },
    "logout_config": {
      "profile_section": "//div[@class='profile']",
      "logout_button": "//a[text()='Logout']"
    },
    "crawlers": {
      "NewsAPICrawler": {
        "filter_category": true,
        "sourceUri": "newspaper.com"
      }
    },
    "scrapers": {
      "TrafilaturaScraper": {
        "trafilatura_kwargs": {
          "prune_xpath": "//div[@class='ads']"
        }
      }
    }
  }
]
```

**Key Fields:**
- `name`: Unique identifier for the subscription
- `domain`: Base URL of the newspaper website
- `paywall`: Boolean indicating if the site has a paywall
- `is_active`: Boolean to enable/disable the subscription
- `login_config`: XPath selectors for automated login process
- `logout_config`: XPath selectors for logout process
- `crawlers`: Configuration for different crawling methods
- `scrapers`: Configuration for content extraction

### 2. Credentials Data (Optional)

**File:** `apps/backend/data/newspapers_accounts.json`

This file contains login credentials for newspaper subscriptions that require authentication.

**Format:**
```json
{
  "CREDENTIALS": {
    "Newspaper Name": {
      "username": "user@example.com",
      "password": "password123"
    },
    "Another Newspaper": {
      "username": "another@example.com",
      "password": "anotherpassword"
    }
  }
}
```

**Notes:**
- The subscription names in the credentials file must exactly match the `name` field in `subscriptions.json`
- This file is optional and only needed for newspapers requiring authentication
- The file is included in `.gitignore` for security reasons
- The `Fernet key` is required for encryption/decryption 

## How to Trigger Data Seeding

Create a .env file with the database credentials.
Navigate to the backend directory and run the seeding script:

```bash
cd apps/backend
python -m app.seed_data
```

## Seeding Process Details

### What Happens During Seeding

1. **Database Connection**: The seeder connects to the configured database
2. **Subscription Seeding**: 
   - Loads data from `subscriptions.json`
   - Updates existing subscriptions or creates new ones based on the `name` field
3. **Credential Seeding** (if credentials file exists):
   - Loads credentials from `newspapers_accounts.json`
   - Matches credentials to subscriptions by name
   - Stores encrypted credentials in the database

### Upsert Behavior

The seeding process uses an "upsert" pattern:
- If a subscription with the same `name` already exists, it will be updated with new values
- If no subscription exists with that name, a new one will be created
- This allows you to safely re-run the seeding process to update configurations

## Prerequisites

Before running the seeding process, ensure:

1. **Database is running**: The PostgreSQL database must be accessible
2. **Environment variables**: Database connection settings are configured
3. **Dependencies installed**: All Python packages are installed (`pip install -r requirements.txt`)
4. **File permissions**: The seeding script has read access to the data files

## Possible Improvements
- Take a snapshot via sql dump of the current state and use it as seeding base
- That way subscriptions and accounts can be stored in the repository which makes automatic seeding possible. (Assuming the Fernet Key does not change)