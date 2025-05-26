# Mediamind

MediaMind is a tool designed to keep client teams informed and prepared by 
delivering daily press reviews. Each morning, it compiles and distributes PDFs
containing curated, anonymized newspaper articles helping teams stay on top of
relevant coverage.

## Project Structure
```
eutop-mediamind/
├── frontend/              # React frontend app
│
├── backend/               # FastAPI backend app
│
├── database/              # Database migrations and configurations
│
├── infra/                 # Infrastructure-as-code
│
├── scripts/               # Project-level scripts
│
├── docs/                  # (Additional) project documentation
│
├── .github/               # GitHub-specific configurations (actions, issue templates)
│
├── .gitignore
│
└── README.md
```

## Guidelines

To ensure a high level of code quality, we have defined a set of [Development Guidelines](./docs/GUIDELINES.md). It is mandatory for everyone working on this repository to adhere to these guidelines. Pull requests may be declined for merge until the code meets our quality standards.

Key areas covered:
- Code style and formatting
- Testing requirements
- Documentation standards

## GitHub Actions

We use GitHub Actions for continuous integration and deployment. Our automated workflows include:

- **Code Quality**: Linting, formatting, and static analysis
- **Testing**: Unit tests, integration tests, and end-to-end tests
- **Deployment**: Automated deployment to staging and production environments

**Important**: Some workflows require environment secrets to be configured in GitHub. Refer to the [official GitHub documentation](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) for setup instructions. Make sure to set all required environment secrets before running the pipeline.

## Monitoring & Error Reporting

This project uses **Sentry** for error monitoring, performance tracing, and session replay in both the frontend and backend.

- **Frontend:**  
  Sentry is integrated via `@sentry/react` and `@sentry/browser`. It automatically captures JavaScript errors, performance metrics, and session replays. Users can also submit bug reports directly from the UI.

- **Backend:**  
  The FastAPI backend uses the Sentry Python SDK to capture unhandled exceptions and performance data, including environment and PII settings.

All errors and performance data are sent to our Sentry project at [csee.sentry.io](https://csee.sentry.io/).
