# EUTOP Mediamind backend

## Commands
Server
   1. `uvicorn app.main:app --reload`: base
   2. options
      1. host: `--host 0.0.0.0`
      2. port: `--port 8000`

You can then see the API definition at `http://localhost:8000/api/docs`
Test
   1. `pytest`: base 
   2. `pytest --cov=app --cov-report=term-missing`: coverage with stdout
   3. `pytest --cov=app --cov-report=html`: coverage with html

## App folder structure
The folder structure was taken from [here](https://github.com/jujumilk3/fastapi-clean-architecture).

- _api_: routing, divided by api version
- _core_: common core configurations
- _repositories_: DB repositories (see "service repository" pattern)
- _services_: services (see "service repository" pattern)
- _utils_: self explanatory


## Sample env
```dotenv
# postgres case
DB=postgresql
DB_USER=myuser
DB_PASSWORD=supersecretpass
DB_HOST=localhost
DB_PORT=5432
```

## Linting and Formatting

- **Black**: Code formatter (run `black .` to format the code)
- **Flake8**: Linter (run `flake8` to check for linting issues)
