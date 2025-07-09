from pydantic_settings import BaseSettings
from typing import Optional

class Config(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: Optional[str] = None

    QUEUE_NAME: str 

    SCHEDULER_INTERVAL: int 

    EMAIL_JOB_INTERVAL: int 
    PIPELINE_JOB_INTERVAL: int

    API_BASE_URL: str 

    class Config:
        env_file = ".env"
        case_sensitive = False
