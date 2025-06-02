# EUTOP Mediamind Backend

## Getting Started

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

## Linting and Formatting

- **Black**: Code formatter (run `black app` to format the code)
- **Isort**: Import sorter (run `isort app` to sort imports)
- **Flake8**: Linter (run `flake8` to check for linting issues)
