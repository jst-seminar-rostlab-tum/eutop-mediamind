from pydantic_settings import BaseSettings


class Config(BaseSettings):
    REDIS_URL: str

    QUEUE_NAME: str

    SCHEDULER_INTERVAL: int

    # Job intervals in seconds. If set to -1 it means the job is disabled.
    EMAIL_JOB_INTERVAL: int
    PIPELINE_JOB_INTERVAL: int
    RSS_JOB_INTERVAL: int
    BREAKING_NEWS_JOB_INTERVAL: int

    API_BASE_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = False
