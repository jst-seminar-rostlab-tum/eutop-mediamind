import logging
from uuid import UUID

import requests
from config import Config
from service import SchedulerService

log = logging.getLogger(__name__)


def schedule_jobs(service: SchedulerService, cfg: Config) -> None:
    log.info("Scheduling jobs...")

    service.schedule_periodic(
        id=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
        every_seconds=cfg.EMAIL_JOB_INTERVAL,
        func=job_request,
        args=[f"{cfg.API_BASE_URL}/v1/jobs/email"],
    )

    service.schedule_periodic(
        id=UUID("4b986edc-360e-4690-8633-ff2f11cdfe3a"),
        every_seconds=cfg.PIPELINE_JOB_INTERVAL,
        func=job_request,
        args=[f"{cfg.API_BASE_URL}/v1/jobs/pipeline"],
    )

    service.schedule_periodic(
        id=UUID("d6b4b98a-9282-4bb0-89d0-09a412a76ab4"),
        every_seconds=cfg.RSS_JOB_INTERVAL,
        func=job_request,
        args=[f"{cfg.API_BASE_URL}/v1/jobs/rss"],
    )

    service.schedule_periodic(
        id=UUID("cc1dface-9213-4eed-8cb2-0edba6b2159c"),
        every_seconds=cfg.BREAKING_NEWS_JOB_INTERVAL,
        func=job_request,
        args=[f"{cfg.API_BASE_URL}/v1/jobs/breaking-news"],
    )


def job_request(url: str, body: dict | None = None) -> None:
    req = requests.post(url, json=body)
    if req.status_code == 200:
        log.info(f"Job status for {url}: {req.json()}")
    else:
        log.error(f"Job failed for: {url} with status code {req.status_code}")
