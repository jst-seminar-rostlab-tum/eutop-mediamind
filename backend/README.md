# EUTOP Mediamind Backend

## Getting started

- Create a virtual environment:
  ```bash
  python -m venv venv
  ```
  Notes:
  - On Windows: Use `python` or `py -3` if you have the Python Launcher
  - On macOS/Linux: Use `python3` if `python` points to Python 2
  - Alternative Windows command: `py -m venv venv`
- Activate the virtual environment:
  - On Windows:
    ```bash
    venv\Scripts\activate
    ```
  - On macOS and Linux:
    ```bash
    source venv/bin/activate
    ```
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Start the server:
  1.  `uvicorn app.main:app --reload`: base
  2.  options
      1. host: `--host 0.0.0.0`
      2. port: `--port 8000`

You can then see the API definition at `http://localhost:8000/api/docs`

- Run tests
  1.  `pytest`: base
  2.  `pytest --cov=app --cov-report=term-missing`: coverage with stdout
  3.  `pytest --cov=app --cov-report=html`: coverage with html

## Docker

### For development

Use the provided [docker-compose.yml](/scripts/docker-compose.dev.yml) file.
From root, execute the following commands to build and start the backend services:

To build the images:

```bash
docker compose build
```

To start the containers:

```bash
docker compose up
```

You can also build and start in one command:

```bash
docker compose up --build
```

### For Production

This approach is mainly for production deployment using terraform (which is why the envs are passed as a JSON), but you can also use it for local development.

To build and run using Docker:

1. Create a `secrets.json` file with your envs:

   ```json
   {
     "API_URL": "https://api.example.com",
     "SENTRY_DSN": "your_sentry_dsn_here"
     // Add other environment variables as needed
   }
   ```

   > This file should contain all the environment variables your application needs, formatted as a JSON object.
   > **Make sure to keep this file secure and do not commit it to version control.**

2. Build the Docker image:

   ```bash
   docker build -t mediamind-backend .
   ```

3. Pass it as an environment variable to the Docker container:
   ```bash
   # Make sure to replace `secrets.json` with the path to your actual secrets file
   docker run -e APP_CONFIG_JSON="$(cat secrets.json)" -p 8000:8000 mediamind-backend
   ```

## App Folder Structure

The folder structure was taken from [here](https://github.com/jujumilk3/fastapi-clean-architecture).

- _api_: routing, divided by api version
- _core_: common core configurations
- _models_: Database models using SQLModel. Reflects the actual DB schema.
- _repositories_: DB repositories responsible for interacting with the database. Follows the "service repository" pattern to abstract query logic.
- _schemas_: Pydantic models for request validation and response serialization. Decouples API data structures from DB models.
- _services_: Business logic layer. Implements domain-specific workflows and delegates persistence to repositories. See "service repository" pattern.
- _utils_: Miscellaneous utilities and helpers (e.g. crawling logic, formatters, converters). Self-explanatory and isolated.

## Secrets Management

We encrypt the credentials for subscriptions before storing them in the database.
These are then decrypted when needed, using the key provided in the environment variables.

Example usage:

```py
from app.models.subscription import Subscription

# Example usage of Subscription model to test encryption/decryption
sub = Subscription(name="Test", domain="example.com", config="{}", scraper_type="test")
sub.secrets = "password123"  # could be anything (e.g., single string, dict, etc.)
print("Subscription (=what's stored in the db):", sub)
print("Decrypted secret:", sub.secrets)
```

```
==> Output
Subscription (=what's stored in the db): name='Test' domain='example.com' config='{}' scraper_type='test' id=UUID('57ea8fcc-e086-4e82-aeef-592ac2823d0e') encrypted_secrets=b'gAAAAABoQA6AfCRBzW-r1fHblfweVb3G6ModxYRKMAKQ6sqWOJDGFc4rRO9o2FF1b1EfpcLpc6wFDGw4eYgKUe2q3H1KQYWdMw=='
Decrypted secret: password123
```

# Database Migration

### Creating new models

Ensure to import newly created models in the following file: alembic/env.py

Alembic is a lightweight database migration tool for use with SQLAlchemy. It allows you to manage changes to your database schema over time, tracking changes via migration scripts.

## Basic Commands

### Create a new migration script

```bash
alembic revision -m "Your message"
```

### Auto-generate migration from model changes

```bash
alembic revision --autogenerate -m "Your message"
```

> Note: Ensure your models reflect the latest state before running this.

### Apply migrations (upgrade)

```bash
alembic upgrade head
```

You can also target a specific version:

```bash
alembic upgrade <revision_id>
```

### Revert migrations (downgrade)

```bash
alembic downgrade -1
```

Or to a specific revision:

```bash
alembic downgrade <revision_id>
```

### Mark the current database state with the latest revision (without running migrations)

```bash
alembic stamp head
```

This is useful when you're starting with an existing database that matches your models but doesn't yet have Alembic version tracking.

### View current migration version

```bash
alembic current
```

### Show the full migration history

```bash
alembic history
```

## Tips

- **Review autogenerated migrations**. Autogenerated migrations might have some issues regarding type conversion or server defaults.
- Maintain **clean, descriptive messages** for each revision.
- Push the migration files to git.

## Linting and Formatting

- **Black**: Code formatter (run `black app` to format the code)
- **Isort**: Import sorter (run `isort app` to sort imports)
- **Flake8**: Linter (run `flake8` to check for linting issues)
