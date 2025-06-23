import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


"""
NOTE: This file is used to load the configuration settings for the application.
It uses Pydantic's BaseSettings to load environment variables and validate
them. It also includes some custom validation logic to ensure that certain
settings are not set to default values in production environments.

IMPORTANT: Please, when adding new environment variables, ensure that they are
documented in the .env.example file and that they are NOT set to default values
in this file. The default values (for local and ci) should be set in the
`.env.example` file, NOT here. Also, don't forget to add them to the validation
checks below. Proper type hinting is also important, as it will help developers
understand the expected type of each environment variable and should be done in
this file. When removing environment variables, ensure that they are removed
from the `.env.example` file, as well as from the validation checks.
"""


class Configs(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENVIRONMENT: Literal["local", "staging", "production", "ci"]
    PROJECT_NAME: str

    # Backend
    SECRET_KEY: str
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ]
    FERNET_KEY: str

    # Postgres
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    SENTRY_DSN: HttpUrl | None

    # Qdrant
    QDRANT_URL: str | None
    QDRANT_API_KEY: str | None
    ARTICLE_VECTORS_COLLECTION: str | None

    # LLMs
    OPENAI_API_KEY: str | None

    # Configuration of the user management tool (Clerk)
    CLERK_SECRET_KEY: str | None
    CLERK_PUBLISHABLE_KEY: str | None
    CLERK_COOKIE_NAME: str

    # AWS
    AWS_ACCESS_KEY_ID: str | None
    AWS_SECRET_ACCESS_KEY: str | None
    AWS_REGION: str | None
    AWS_S3_BUCKET_NAME: str | None

    # NewsAPI AI
    NEWSAPIAI_API_KEY: str | None

    DISABLE_AUTH: bool = False

    # Email
    MAX_EMAIL_ATTEMPTS: int
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        # Remove port from host if present
        host = self.POSTGRES_SERVER.split(":")[0]
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=host,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        if self.ENVIRONMENT == "local":
            return ["*"]
        return [
            str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS
        ]

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if (
            value is None
            or value == "changethis"
            or "example" in value.lower()
        ):
            message = (
                f'The value of {var_name} is "{value}", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        # Skip checks in CI environment
        if self.ENVIRONMENT == "ci":
            return self

        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("FERNET_KEY", self.FERNET_KEY)
        self._check_default_secret("POSTGRES_SERVER", self.POSTGRES_SERVER)
        self._check_default_secret("POSTGRES_DB", self.POSTGRES_DB)
        self._check_default_secret("POSTGRES_USER", self.POSTGRES_USER)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("CLERK_SECRET_KEY", self.CLERK_SECRET_KEY)
        self._check_default_secret(
            "CLERK_PUBLISHABLE_KEY", self.CLERK_PUBLISHABLE_KEY
        )
        self._check_default_secret("CLERK_COOKIE_NAME", self.CLERK_COOKIE_NAME)
        self._check_default_secret("AWS_ACCESS_KEY_ID", self.AWS_ACCESS_KEY_ID)
        self._check_default_secret(
            "AWS_SECRET_ACCESS_KEY", self.AWS_SECRET_ACCESS_KEY
        )
        self._check_default_secret("AWS_REGION", self.AWS_REGION)
        self._check_default_secret(
            "AWS_S3_BUCKET_NAME", self.AWS_S3_BUCKET_NAME
        )
        self._check_default_secret("QDRANT_URL", self.QDRANT_URL)
        self._check_default_secret("QDRANT_API_KEY", self.QDRANT_API_KEY)
        self._check_default_secret(
            "ARTICLE_VECTORS_COLLECTION", self.ARTICLE_VECTORS_COLLECTION
        )
        self._check_default_secret("SMTP_SERVER", self.SMTP_SERVER)
        self._check_default_secret("SMTP_USER", self.SMTP_USER)
        self._check_default_secret("SMTP_PASSWORD", self.SMTP_PASSWORD)

        return self

    @model_validator(mode="after")
    def validate_auth_in_production(self) -> Self:
        # Ensure authentication is not disabled in production or staging.
        if self.ENVIRONMENT in ("production", "staging") and self.DISABLE_AUTH:
            raise ValueError(
                f"DISABLE_AUTH cannot be True in {self.ENVIRONMENT} "
                "environment. This would be a severe security risk."
            )
        # Log warning for non-production environments.
        elif self.DISABLE_AUTH:
            warnings.warn(
                "Authentication is disabled by DISABLED_AUTH in "
                f"{self.ENVIRONMENT} environment. Never use this "
                "setting in production.",
            )
        return self


configs = Configs()
