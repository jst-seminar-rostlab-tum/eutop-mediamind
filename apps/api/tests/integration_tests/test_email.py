from unittest.mock import patch

import pytest

from app.models.email import EmailState
from app.repositories.email_repository import EmailRepository
from app.services.email_service import EmailSchedule, EmailService


@pytest.mark.skip(reason="no way of currently testing this")
async def test_schedule_email():
    # Arrange
    email_schedule = EmailSchedule(
        "test@test.com",
        "Test Subject",
        "text/plain",
        "This is a test email.",
        "attachment",
    )

    # Act
    scheduled_email = await EmailService.schedule_email(email_schedule)

    # Assert
    assert scheduled_email.recipient == email_schedule.recipient
    assert scheduled_email.subject == email_schedule.subject
    assert scheduled_email.content_type == email_schedule.content_type
    assert scheduled_email.content == email_schedule.content
    assert scheduled_email.attachment == email_schedule.attachment
    assert scheduled_email.state == EmailState.PENDING
    assert scheduled_email.attempts == 0


@pytest.mark.skip(reason="no way of currently testing this")
async def test_send_scheduled_emails():
    # Arrange
    email_schedule = EmailSchedule(
        "rec@mail.com",
        "Test Subject",
        "text/plain",
        "This is a test email.",
        "attachment",
    )

    # Act
    with patch.object(
        EmailService, "_EmailService__send_email", return_value=None
    ):
        scheduled_email = await EmailService.schedule_email(email_schedule)
        await EmailService.send_scheduled_emails()

    email = await EmailRepository.get_email_by_id(scheduled_email.id)

    # Assert
    assert email is not None
    assert email.state == EmailState.SENT
    assert email.attempts == 1
