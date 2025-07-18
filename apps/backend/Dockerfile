# ---------- Base build stage ----------
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ---------- Final stage ----------
FROM python:${PYTHON_VERSION}-slim

# Create a non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install runtime dependencies including Chrome for Selenium
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    jq \
    wget \
    gnupg \
    ca-certificates \
    gettext\
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    curl gnupg wget unzip xvfb libgbm1 \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxkbcommon0 libatspi2.0-0 libxdamage1 libpango-1.0-0 \
    libcairo2 libasound2 libsecret-1-0 libgles2 \
    libgtk-3-0 libgdk-pixbuf2.0-0 libpangocairo-1.0-0 libcairo-gobject2 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Run translations
RUN msgfmt app/services/locales/de/LC_MESSAGES/translations.po \
    -o app/services/locales/de/LC_MESSAGES/translations.mo

# Copy entrypoint and set permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install browsers to project dir to avoid permission issues in Docker
ENV PLAYWRIGHT_BROWSERS_PATH=0
# Chromium & crawl4ai final setup
RUN playwright install chromium && crawl4ai-setup

# Set permissions and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port if needed (e.g. for web app)
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
