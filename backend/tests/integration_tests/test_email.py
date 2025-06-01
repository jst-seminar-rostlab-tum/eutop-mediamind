from app.services.email_service import EmailService, EmailSchedule

async def test_schedule_email():
    # Arrange
    email_schedule = EmailSchedule("test@test.com", "Test Subject", "text/plain", "This is a test email.", "attachment")

    # Act
    scheduled_email = await EmailService.schedule_email(email_schedule)

    # Assert
    assert scheduled_email.recipient == email_schedule.recipient
    assert scheduled_email.subject == email_schedule.sub
    assert scheduled_email.content_type == email_schedule.content_type
    assert scheduled_email.content == email_schedule.content
    assert scheduled_email.attachment == email_schedule.attachment





