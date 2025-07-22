# 1%
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.email import Email
from app.services.email_service import EmailSchedule, EmailServer, EmailService


@pytest.mark.asyncio
def test_create_email():
    email = EmailService.create_email(
        "to@test.com", "subject", "html", "<b>content</b>"
    )
    assert email.recipient == "to@test.com"
    assert email.subject == "subject"
    assert email.content_type == "html"
    assert email.content == "<b>content</b>"


@pytest.mark.asyncio
def test_create_ses_email_server():
    server = EmailService.create_ses_email_server()
    assert isinstance(server, EmailServer)


@pytest.mark.asyncio
async def test_schedule_email(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.email_repository.EmailRepository.add_email",
        AsyncMock(return_value=MagicMock()),
    )
    schedule = EmailSchedule(
        recipient="to@test.com", subject="s", content="c", content_type="html"
    )
    result = await EmailService.schedule_email(schedule)
    assert result is not None


@pytest.mark.asyncio
async def test_send_email(monkeypatch):
    monkeypatch.setattr(
        "app.services.email_service.EmailService._EmailService__send_email",
        AsyncMock(),
    )
    email = MagicMock(spec=Email)
    email.sender = "from@test.com"
    email.recipient = "to@test.com"
    email.subject = "subject"
    email.content = "<b>content</b>"
    email.id = 1
    await EmailService.send_email(
        email, pdf_bytes=None, bcc_recipients=["bcc@test.com"]
    )


@pytest.mark.asyncio
def test__render_email_template(monkeypatch):
    monkeypatch.setattr(
        "app.services.email_service.templates_env", MagicMock()
    )
    monkeypatch.setattr(
        "app.services.email_service.templates_env.get_template",
        MagicMock(
            return_value=MagicMock(render=MagicMock(return_value="html"))
        ),
    )
    result = EmailService._render_email_template("template.html", {"a": 1})
    assert result == "html"
