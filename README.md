# Mediamind

MediaMind is a tool designed to keep client teams informed and prepared by
delivering daily press reviews. Each morning, it compiles and distributes PDFs
containing curated, anonymized newspaper articles helping teams stay on top of
relevant coverage.

## Guidelines

To ensure a high level of code quality, we have defined a set of [Development Guidelines](./docs/GUIDELINES.md). It is mandatory for everyone working on this repository to adhere to these guidelines. Pull requests may be declined for merge until the code meets our quality standards.

Key areas covered:
- Code style and formatting
- Testing requirements (for Backend and Frontend)
- Documentation standards

## Project Structure

```
eutop-mediamind/
│
├── .github/               # GitHub-specific configurations (actions, issue templates)
│
├── backend/               # FastAPI backend app
│
├── docs/                  # (Additional) project documentation
│
├── frontend/              # React frontend app
│
├── infra/                 # Infrastructure-as-code
│
├── scripts/               # Project-level scripts
│
├── .gitignore
│
└── README.md
```

## Development Setup
For detailed setup instructions and development workflows, refer to the component-specific documentation:

- **[Backend](./backend/README.md)** - FastAPI server, API documentation
- **[Frontend](./frontend/README.md)** - React app, component library
- **[Infrastructure](./infra/README.md)** - AWS deployment, Terraform configs

### Prerequisites
- **Node.js 22+** - For frontend development
- **Python 3.13+** - For backend development
- **AWS CLI** and **openTofu** - For infrastructure as code (optional)

### Environment Configuration

Copy the example environment files and configure them for your setup:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Refer to each component's README for specific environment variable requirements.
**Important:** Keep this file up to date, so whenever you add/remove a (new) environment variable, also add it with a **DUMMY** value to the respective `.env.example` file. Otherwise it's harder for other developers to understand which variables where added/removed by you.

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

## Vector Database (Qdrant)

The project uses **Qdrant** as a vector database for efficient storage and retrieval of document embeddings. You can access the Qdrant dashboard locally by navigating to [http://localhost:6333/dashboard](http://localhost:6333/dashboard) after starting the Qdrant service (via Docker Compose).
