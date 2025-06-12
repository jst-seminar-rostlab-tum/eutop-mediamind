"""
NOTE:
This is just a testing controller for sending emails and creating PDFs.
Once we have a proper scheduler, we can remove this controller.
"""
from fastapi import APIRouter, Depends

import base64
from app.services.email_service import EmailService, EmailSchedule
from app.services.pdf_service import PDFService
from app.core.auth import get_authenticated_user

router = APIRouter(
    prefix="/emails",
    tags=["emails"],
)

@router.get("/smart")
async def trigger_email_sending_with_matching(current_user=Depends(get_authenticated_user)):
    pdf_bytes = await PDFService.create_pdf_for_user(current_user)
    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)

    # email_schedule = EmailSchedule(
    #     recipient=current_user.email,
    #     subject="[MEDIAMIND] Your daily report",
    #     content_type="text/plain",
    #     content="Dear user,\nPlease find your daily news report attached.\nBest regards,\nMediaMind Team",
    #     attachment=base64.b64encode(pdf_bytes).decode('utf-8')
    # )
    #
    # await EmailService.schedule_email(email_schedule)
    # await EmailService.send_scheduled_emails()
    return {"message": "Email scheduled and sent successfully."}

# @router.get("/{recipient_email}")
# async def trigger_email_sending(recipient_email: str):
#     pdf_bytes = await PDFService.create_sample_pdf()
#
#     email_schedule = EmailSchedule(
#         recipient=recipient_email,
#         subject="[MEDIAMIND] Your daily report",
#         content_type="text/plain",
#         content="Dear user,\nPlease find your daily news report attached.\nBest regards,\nMediaMind Team",
#         attachment=base64.b64encode(pdf_bytes).decode('utf-8')
#     )
#
#     await EmailService.schedule_email(email_schedule)
#     await EmailService.send_scheduled_emails()
#     return {"message": "Email scheduled and sent successfully."}

@router.get("/pdf")
async def trigger_pdf_creation():
    pdf_bytes = await PDFService.create_sample_pdf()

    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)


