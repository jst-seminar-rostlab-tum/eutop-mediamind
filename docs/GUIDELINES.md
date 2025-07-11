# Quality Control: Coding Guidelines

## Linting & Formatting

**Linter:** Fix all Linter/Typechecker warnings/errors before committing code.

**Formatter:** Turn on “format on save” in your IDE settings.

### VSCode

Install the required extensions:

- Frontend:
  - [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)
  - [ESlint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
- Backend:
  - [Black](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
  - [Flake8](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8)
  - [isort](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)

Change the settings in VSCode to look for the config files of Linter and Formatter in the `backend/` or `frontend/` directory of the project, respectively. Then turn on “format on save”, also in the settings.

### PyCharm

Install **black** & **isort** and add them to the FileWatchers.
This automatically formats the code according to PEP 8 when saving the files.

## Backend

### Code Style

Adhere to the [PEP 8](https://peps.python.org/pep-0008/) style guide:

- **Indentation**: 4 spaces per indentation level.
- **Line Length**: Limit lines to 79 characters.
- **Imports**: Group and order imports as follows:
  - Standard library imports.
  - Related third-party imports.
  - Local application/library-specific imports

Each group should be separated by a blank line.

- **Naming Conventions**:
  - Variables, functions, methods: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

### Comments & Docstrings

- **Docstrings**: Use triple double quotes (`"""`) for module, class, and function docstrings. Follow the [PEP 257](https://peps.python.org/pep-0257/) conventions.
- **Inline Comments**:
  - Use sparingly to explain non-obvious code.
  - Separate inline comments by at least two spaces from the statement.
  - Start with a `#` and a single space.
  - Ensure they are complete sentences and start with a capital letter.

### Testing

- **Framework**: Use [pytest](https://docs.pytest.org/) for writing and running tests.
- **Test Structure**: Place tests in a `tests/` in the `backend/` directory, mirroring the structure of it.
- **Test Naming**: Prefix test functions with `test_` and use descriptive names to indicate their purpose.

## Frontend

### Code Style

Follow the [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html):

- **Indentation**: 2 spaces per indentation level.
- **Line Length**: Limit lines to 100 characters.
- **Semicolons**: Always use semicolons at the end of statements.
- **Naming Conventions**:
  - Variables, functions, methods: `camelCase`
  - Classes, interfaces, enums: `PascalCase`
  - Constants: `UPPER_CASE`
- **Interfaces**: Do not prefix interface names with `I`.

### Comments & Documentation

- **Documentation Comments**: Use [JSDoc](https://jsdoc.app/) style comments for functions, classes, and interfaces.
- **Inline Comments**:
  - Use `//` for single-line comments and `/* */` for multi-line comments.
  - Ensure comments are clear and concise.
  - Avoid redundant comments that restate the code.

### Testing

- **Framework**: Use [Jest](https://jestjs.io/) for unit testing.
- **Test Structure**: Place tests in a `tests/` in the `frontend/` directory, mirroring the structure of it.
- **Test Naming**: Use descriptive names for test files and functions, reflecting the functionality being tested.

## CI/CD

Before merging a PR (in both Frontend and Backend), the pre-merge pipeline must successfully execute. This pipeline will:

- Enforce the compliance of the new code with the relative linter configuration.
- Ensure that the code builds without errors.
- Execute unit, integration and e2e tests to ensure that the new feature does not break existent code.
- (TBD) Ensure Docker is able to build an image from the codebase.

## Version Control & Collaboration

### Branching Strategy

Use feature branches named using the pattern `type/short-description`, e.g., `feat/backend-setup`. The type can be:

- `feat`: the branch introduces a new feature.
- `fix`: the branch fixes a bug.
- `docs`: the branch contains documentation
- `release`: the branch is needed for the release process

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- Format: `<type>(<scope>): <description>`
- Example: `feat(auth): add login functionality`

### Pull Requests

- Use the corresponding **frontend** or **backend** labels for better filtering and categorization of the PRs.
- Ensure all checks pass before requesting a review.
- Include a clear description of the changes and any relevant context.
- Link related issues or tasks to keep track.

See also: [Better Git Practices](https://nutritious-request-5b4.notion.site/Student-Resources-WIP-a328da1665194638ae2f694bf127727f#09174eaa615c4658bfda117bd320a13b)

## Documentation

Reflect any updates to the steps required for setup or any part of it, core parts of the functionality or usability as described, or technologies used in the README.md file. The README.md file should grow as the project does and always provide an up-to-date overview of the project, how to set it up locally, and how to use it.
