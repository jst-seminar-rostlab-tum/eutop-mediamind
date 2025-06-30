# flake8: noqa: E501
from uuid import UUID
"""
NOTE:
This is just a testing controller for sending emails and creating PDFs.
Once we have a proper scheduler, we can remove this controller.
"""

import uuid
from time import gmtime, strftime

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends

from app.services.email_service import EmailSchedule, EmailService
from app.services.report_service import ReportService
from app.services.s3_service import S3Service, get_s3_service
from app.services.search_profiles_service import SearchProfileService
from app.services.user_service import UserService
from app.services.translation_service import ArticleTranslationService

router = APIRouter(
    prefix="/emails",
    tags=["emails"],
)


@router.get("/send/{recipient_email}")
async def trigger_email_sending(recipient_email: str):
    email_schedule = EmailSchedule(
        recipient=recipient_email,
        subject="[MEDIAMIND] Your daily report",
        content_type="text/HTML",
        content=build_email_content(
            "<test_s3_link>", "<test_dashboard_link>", "<Test Search Profile>"
        ),
    )

    await EmailService.schedule_email(email_schedule)
    await EmailService.send_scheduled_emails()
    return {"message": "Email scheduled and sent successfully."}


@router.get("/test")
async def send_report_email(
    clerk_id: str = Query(..., description="Clerk User ID"),
    search_profile_id: str = Query(..., description="Search Profile UUID"),
    s3_service: S3Service = Depends(get_s3_service),
):
    print(
        f"Sending report email for user {clerk_id} and search profile {search_profile_id}"
    )

    try:
        search_profile_id = uuid.UUID(search_profile_id)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid search_profile_id UUID format"
        )
    timeslot = "morning"

    # Get user and check if found
    user = await UserService.get_by_clerk_id(clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    search_profile = await SearchProfileService.get_extended_by_id(
        search_profile_id, current_user=user
    )
    if not search_profile:
        raise HTTPException(status_code=404, detail="SearchProfile not found")
    
    language = search_profile.language

    # Get or create report
    report = await ReportService.get_or_create_report(
        search_profile.id, timeslot, language, s3_service
    )
    if not report:
        raise HTTPException(
            status_code=500, detail="Could not create or retrieve report"
        )

    # Prepare email
    presigned_url = s3_service.generate_presigned_url(
        key=report.s3_key, expires_in=604800  # 7 days
    )
    dashboard_url = (
        f"https://mediamind.csee.tech/dashboard/reports/{report.id}"
    )

    translator = ArticleTranslationService.get_translator(language)
    time_slot_translated = translator(report.time_slot.capitalize())
    subject = (
        f"[MEDIAMIND] {translator('Your')} {time_slot_translated} "
        f"{translator('Report')} {translator('for')} {search_profile.name}"
    )
    # Use the actual search profile name in the email content
    email_schedule = EmailSchedule(
        recipient=user.email,
        subject=subject,
        content_type="text/HTML",
        content=EmailService.build_email_content(
            presigned_url, dashboard_url, search_profile.name, user.last_name, language
        ),
    )

    await EmailService.schedule_email(email_schedule)
    await EmailService.send_scheduled_emails()
    return {"message": "Email scheduled and sent successfully."}
