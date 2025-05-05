# Backend

Directory containing backend services and packages.

## Setup

- Create a virtual environment:

  ```bash
  python -m venv venv
  ```

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

- Run the example script:

  ```bash
  python main.py
  ```

## Linting and Formatting

- **Black**: Code formatter (run `black src` to format the code)
- **Isort**: Import sorter (run `isort src` to sort imports)
- **Flake8**: Linter (run `flake8` to check for linting issues)
