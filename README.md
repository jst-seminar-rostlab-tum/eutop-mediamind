# Mediamind

MediaMind is a tool designed to keep client teams informed and prepared by
delivering daily press reviews. Each morning, it compiles and distributes PDFs
containing curated, anonymized newspaper articles helping teams stay on top of
relevant coverage.

## Project Structure

```
eutop-mediamind/
├── frontend/              # Frontend app
│
├── backend/               # Backend app
│
├── database/              # DB migrations and configs
│
├── infra/                 # Infrastructure
│
├── scripts/               # Project-level scripts
│
├── docs/                  # Documentation
│
├── .github/               # GitHub-specific configs (actions, issue templates)
│
├── .gitignore
│
└── README.md
```

## Monitoring & Error Reporting

This project uses **Sentry** for error monitoring, performance tracing, and session replay in both the frontend and backend.

- **Frontend:**  
  Sentry is integrated via `@sentry/react` and `@sentry/browser`. It automatically captures JavaScript errors, performance metrics, and session replays. Users can also submit bug reports directly from the UI.

- **Backend:**  
  The FastAPI backend uses the Sentry Python SDK to capture unhandled exceptions and performance data, including environment and PII settings.

All errors and performance data are sent to our Sentry project at [csee.sentry.io](https://csee.sentry.io/).

## Vector Database (Qdrant)

The project uses **Qdrant** as a vector database for efficient storage and retrieval of document embeddings. You can access the Qdrant dashboard locally by navigating to [http://localhost:6333/dashboard](http://localhost:6333/dashboard) after starting the Qdrant service (via Docker Compose).

## Licence

TODO
