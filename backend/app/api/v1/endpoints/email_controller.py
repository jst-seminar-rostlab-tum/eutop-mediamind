"""
NOTE:
This is just a testing controller for sending emails and creating PDFs.
Once we have a proper scheduler, we can remove this controller.
"""

import base64

from fastapi import APIRouter

from app.services.email_service import EmailSchedule, EmailService
from app.services.pdf_service import PDFService

router = APIRouter(
    prefix="/emails",
    tags=["emails"],
)


@router.get("/{recipient_email}")
async def trigger_email_sending(recipient_email: str):
    pdf_bytes = await PDFService.create_sample_pdf()

    email_schedule = EmailSchedule(
        recipient=recipient_email,
        subject="[MEDIAMIND] Your daily report",
        content_type="text/plain",
        content="""
            Dear user,
            Please find your daily news report attached.

            Best regards,
            MediaMind Team
        """,
        attachment=base64.b64encode(pdf_bytes).decode("utf-8"),
    )

    await EmailService.schedule_email(email_schedule)
    await EmailService.send_scheduled_emails()
    return {"message": "Email scheduled and sent successfully."}


@router.get("/pdf")
async def trigger_pdf_creation():
    pdf_bytes = await PDFService.create_sample_pdf()

    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)
