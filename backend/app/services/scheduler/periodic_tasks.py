from app.services.email_service import EmailService
from .scheduler_service import SchedulerService

def register_periodic_tasks():
    _schedule_periodic_email_sending()

def _schedule_periodic_email_sending():
    SchedulerService.schedule_periodic(
        every_seconds=60 * 30,  # Every 30 minutes
        func=EmailService.email_job,
    )
