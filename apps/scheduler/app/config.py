from pydantic_settings import BaseSettings


class Config(BaseSettings):
    REDIS_URL: str

    QUEUE_NAME: str

    SCHEDULER_INTERVAL: int

    # Job intervals in seconds. If set to -1 it means the job is disabled.
    EMAIL_JOB_INTERVAL: int
    RSS_JOB_INTERVAL: int
    BREAKING_NEWS_JOB_INTERVAL: int

    # Pipeline job schedule configuration
    PIPELINE_MORNING_TIME: str = "10:00"
    PIPELINE_AFTERNOON_TIME: str = "16:00"
    PIPELINE_EVENING_TIME: str = "21:00"
    PIPELINE_MORNING_LABEL: str = "morning"
    PIPELINE_AFTERNOON_LABEL: str = "afternoon"
    PIPELINE_EVENING_LABEL: str = "evening"

    API_BASE_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = False
