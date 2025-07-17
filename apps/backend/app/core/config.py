"""
Configuration Management Module

This module provides centralized configuration management for the EUTOP
application using Pydantic's BaseSettings for environment variable loading
and validation.

Key Features:
- Type-safe configuration with Pydantic validation
- Environment-specific validation (stricter in production)
- Lazy initialization for better testing support
- Comprehensive security checks for sensitive values

Usage:
    from app.core.config import get_configs
    configs = get_configs()

Environment Variables:
    All configuration values should be provided via environment variables.
    See .env.example for the complete list of required variables.

Security:
    - Never commit real secrets to version control
    - Use 'changethis' or 'example' values in .env.example
    - The system will warn/error if default values are used in production

IMPORTANT: When adding new environment variables:
1. Add them to this class with proper type hints
2. Document them in .env.example with example values
3. Add validation in _enforce_non_default_secrets if sensitive
4. Never set real default values here - only in .env.example
"""

import json
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    Field,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

from app.core.logger import get_logger

logger = get_logger(__name__)


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Configs(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True
    )

    # Core Application Settings
    ENVIRONMENT: Literal["local", "staging", "production", "ci"]
    PROJECT_NAME: str

    # Backend Security
    SECRET_KEY: str
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ]
    FERNET_KEY: str

    # Database Configuration
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Monitoring
    SENTRY_DSN: str

    # Cache & Storage
    REDIS_URL: str

    # Vector Database
    QDRANT_URL: str
    QDRANT_API_KEY: str
    ARTICLE_VECTORS_COLLECTION: str

    # AI Services
    OPENAI_API_KEY: str

    # Authentication (Clerk)
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_COOKIE_NAME: str

    # Cloud Storage (AWS)
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET_NAME: str

    # External APIs
    NEWSAPIAI_API_KEY: str

    # Feature Flags
    DISABLE_AUTH: bool = Field(default=False)

    # Email Configuration
    MAX_EMAIL_ATTEMPTS: int
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str

    # Chatbot Email Configuration
    CHAT_API_KEY: str
    CHAT_SMTP_SERVER: str
    CHAT_SMTP_PORT: int
    CHAT_SMTP_USER: str
    CHAT_SMTP_FROM: EmailStr
    CHAT_SMTP_PASSWORD: str

    # API Documentation
    API_SERVER_INFOS: str = Field(default="[]")

    # Network Configuration
    PROXY_URL: str

    @computed_field
    @property
    def API_SERVERS(self) -> list[dict[str, str]]:
        try:
            servers = json.loads(self.API_SERVER_INFOS)
            if isinstance(servers, list):
                return [
                    s
                    for s in servers
                    if isinstance(s, dict)
                    and "url" in s
                    and "description" in s
                ]
            return []
        except Exception:
            return []

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        Build PostgreSQL connection URI from individual components.
        Handles cases where port might be included in server string.
        """
        # Remove port from host if present
        host = self.POSTGRES_SERVER.split(":")[0]
        url = MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=host,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )
        return PostgresDsn(str(url))

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        """
        Get all CORS origins based on environment.
        Local environment allows all origins for development.
        """
        if self.ENVIRONMENT == "local":
            return ["*"]
        return [
            str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS
        ]

    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT in ("local", "ci")

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """
        Check if a configuration value is set to a default/insecure value.

        Args:
            var_name: Name of the configuration variable
            value: Value to check

        Raises:
            ValueError: If the value is insecure and environment is not local
        """
        if (
            value is None
            or value == "changethis"
            or "example" in value.lower()
            or value == ""
        ):
            message = (
                f'The value of {var_name} is "{value}", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                logger.warning(message)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """
        Validate that security-sensitive configuration values are not set to
        defaults. Skips validation in CI environment for testing purposes.
        """
        # Skip checks in CI environment
        if self.ENVIRONMENT == "ci":
            return self

        # Core security settings
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("FERNET_KEY", self.FERNET_KEY)

        # Database settings
        self._check_default_secret("POSTGRES_SERVER", self.POSTGRES_SERVER)
        self._check_default_secret("POSTGRES_DB", self.POSTGRES_DB)
        self._check_default_secret("POSTGRES_USER", self.POSTGRES_USER)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)

        # Authentication settings
        self._check_default_secret("CLERK_SECRET_KEY", self.CLERK_SECRET_KEY)
        self._check_default_secret(
            "CLERK_PUBLISHABLE_KEY", self.CLERK_PUBLISHABLE_KEY
        )
        self._check_default_secret("CLERK_COOKIE_NAME", self.CLERK_COOKIE_NAME)

        # Cloud storage settings
        self._check_default_secret("AWS_ACCESS_KEY_ID", self.AWS_ACCESS_KEY_ID)
        self._check_default_secret(
            "AWS_SECRET_ACCESS_KEY", self.AWS_SECRET_ACCESS_KEY
        )
        self._check_default_secret("AWS_REGION", self.AWS_REGION)
        self._check_default_secret(
            "AWS_S3_BUCKET_NAME", self.AWS_S3_BUCKET_NAME
        )

        # External services
        self._check_default_secret("REDIS_URL", self.REDIS_URL)
        self._check_default_secret("QDRANT_URL", self.QDRANT_URL)
        self._check_default_secret("QDRANT_API_KEY", self.QDRANT_API_KEY)
        self._check_default_secret(
            "ARTICLE_VECTORS_COLLECTION", self.ARTICLE_VECTORS_COLLECTION
        )

        # Email settings
        self._check_default_secret("SMTP_SERVER", self.SMTP_SERVER)
        self._check_default_secret("SMTP_USER", self.SMTP_USER)
        self._check_default_secret("SMTP_PASSWORD", self.SMTP_PASSWORD)

        # Chatbot email settings
        self._check_default_secret("CHAT_API_KEY", self.CHAT_API_KEY)
        self._check_default_secret("CHAT_SMTP_SERVER", self.CHAT_SMTP_SERVER)
        self._check_default_secret("CHAT_SMTP_USER", self.CHAT_SMTP_USER)
        self._check_default_secret("CHAT_SMTP_FROM", self.CHAT_SMTP_FROM)
        self._check_default_secret(
            "CHAT_SMTP_PASSWORD", self.CHAT_SMTP_PASSWORD
        )

        # External APIs
        self._check_default_secret("NEWSAPIAI_API_KEY", self.NEWSAPIAI_API_KEY)
        self._check_default_secret("OPENAI_API_KEY", self.OPENAI_API_KEY)

        # Network Configuration
        self._check_default_secret("PROXY_URL", self.PROXY_URL)

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
            logger.warning(
                "Authentication is disabled by DISABLED_AUTH in "
                f"{self.ENVIRONMENT} environment. Never use this "
                "setting in production.",
            )
        return self


_configs_instance: "Configs | None" = None


def get_configs() -> "Configs":
    """
    Get the global configuration instance.
    """
    global _configs_instance
    if _configs_instance is None:
        _configs_instance = Configs()  # type: ignore[call-arg]
    return _configs_instance


def reset_configs() -> None:
    """Reset the global configuration instance. Useful for testing."""
    global _configs_instance
    _configs_instance = None
