# Mediamind

MediaMind is a tool designed to keep client teams informed and prepared by
delivering daily press reviews. Each morning, it compiles and distributes PDFs
containing curated, anonymized newspaper articles helping teams stay on top of
relevant coverage.

## Environments & API Endpoints

MediaMind is deployed in two main environments, each with its own API, database, and authentication configuration:

### Production

- **Frontend:** [mediamind.csee.tech](https://mediamind.csee.tech)
- **API:** [api.mediamind.csee.tech](https://api.mediamind.csee.tech)
- **Clerk:** Live mode

### Development

- **Frontend:** Vercel preview deployments or local development
- **API:** [dev.api.mediamind.csee.tech](https://dev.api.mediamind.csee.tech)
- **Clerk:** Test mode

### Proxy Routing

To simplify local development and testing, the following proxy routes are available via [mediamind.csee.tech](https://mediamind.csee.tech):

- `/api/*` → `api.mediamind.csee.tech/api/*`
- `/dev/api/*` → `dev.api.mediamind.csee.tech/api/*`

**Example:**  
A request to [mediamind.csee.tech/dev/api/v1/healthcheck](https://mediamind.csee.tech/dev/api/v1/healthcheck) is proxied to [dev.api.mediamind.csee.tech/api/v1/healthcheck](https://dev.api.mediamind.csee.tech/api/v1/healthcheck)

> **Note:**
>
> - All Vercel preview deployments use the development environment.
> - Only [mediamind.csee.tech](https://mediamind.csee.tech) uses the production environment.
> - For authentication, Clerk cookies set on `localhost` are not sent to other domains (such as `*.mediamind.csee.tech`). To test authentication with the dev API, use a Vercel preview or run your backend locally.

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

## Vector Database (Qdrant)

The project uses **Qdrant** as a vector database for efficient storage and retrieval of document embeddings. You can access the Qdrant dashboard locally by navigating to [http://localhost:6333/dashboard](http://localhost:6333/dashboard) after starting the Qdrant service (via Docker Compose).
