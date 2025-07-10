import requests
from config import Config
from service import SchedulerService
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

def schedule_jobs(service: SchedulerService, cfg: Config) -> None:
    logger.info("Scheduling jobs...", cfg.EMAIL_JOB_INTERVAL)

    service.schedule_periodic(
        id = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
        every_seconds= cfg.EMAIL_JOB_INTERVAL,
        func = job_request,
        args =[f"{cfg.API_BASE_URL}/v1/jobs/email"],
    )

    service.schedule_periodic(
        id = UUID("4b986edc-360e-4690-8633-ff2f11cdfe3a"),
        every_seconds= cfg.PIPELINE_JOB_INTERVAL,
        func = job_request,
        args =[f"{cfg.API_BASE_URL}/v1/jobs/pipeline"],
    )


def job_request(url: str, body: dict|None = None) -> None:
    req = requests.post(url, json=body)
    if req.status_code == 200:
        logger.info(f"Job status for {url}: {req.json()}")
    else:
        logger.error(f"Job failed for: {url} with status code {req.status_code}")
