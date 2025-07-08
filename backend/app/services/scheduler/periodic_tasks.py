from app.services.email_service import EmailService
from app.services import pipeline
from .scheduler_service import SchedulerService
from uuid import UUID
from datetime import datetime, date

def register_periodic_tasks():
    _schedule_periodic_email_sending()
    _schedule_pipeline()

def _schedule_periodic_email_sending():
    SchedulerService.schedule_periodic(
        id=UUID("06bfb6b9-7316-4b7d-b503-993456272a30"),
        every_seconds=60 * 30,  # Every 30 minutes
        func=EmailService.email_job,
    )

def _schedule_pipeline():
    start = datetime.combine(date.today(), datetime.min.time())
    end = datetime.now()
    language = "en",

    SchedulerService.schedule_periodic(
        id=UUID("d1f8b5c2-3e4f-4a6b-8c9d-0e1f2a3b4c5d"),
        every_seconds=60 * 60 * 12,  # Every 12 hours
        func=pipeline.run,
        args=[start, end, language],
    )
