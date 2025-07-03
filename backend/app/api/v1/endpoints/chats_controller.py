import re

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.core.config import configs
from app.services.email_service import EmailService
from app.services.user_service import UserService
from app.models.email import Email

router = APIRouter(
    prefix="/chats",
    tags=["chats"],
)


class ChatRequest(BaseModel):
    sender: str
    subject: str
    body: str
    s3_key: str
    bucket: str


def extract_email_address(sender: str) -> str:
    """
    Extracts the email address from a sender string like:
    'John Doe <john.doe@example.com>' -> 'john.doe@example.com'
    or 'John Doe john.doe@example.com' -> 'john.doe@example.com'
    If no email is found, returns the original string.
    """
    # Try angle brackets first
    match = re.search(r"<([^>]+)>", sender)
    if match:
        return match.group(1).strip()
    # Try to find a plain email address
    match = re.search(
        r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", sender
    )
    if match:
        return match.group(1).strip()
    return sender.strip()


@router.post("/")
async def receive_chat(
    chat: ChatRequest,
    x_api_key: str = Header(None, alias="x-api-key"),
):
    if x_api_key != configs.CHAT_API_KEY:
        raise HTTPException(
            status_code=401, detail="Invalid or missing API key"
        )

    # Extract just the email address from the sender field
    sender_email = extract_email_address(chat.sender)

    # Check if user exists
    user = await UserService.get_by_email(sender_email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with email {sender_email} not found.",
        )

    email = Email(
        sender=configs.SMTP_USER,
        recipient=user.email,
        subject=f"[MEDIAMIND] RE: {chat.subject}",
        content_type="text/HTML",
        content=f"""<p>Hi {user.first_name},</p>
        Congratulations on using the slowest, most unsecure and least
        scalable web chatbot in the world!</p>
        <p><strong>Subject:</strong> {chat.subject}</p>
        <p><strong>Message:</strong> {chat.body}</p>
        Plese use chatgpt, claude, or any other AI chatbot instead:
        <p><a href="https://chat.openai.com/">ChatGPT</a> |
        <a href="https://claude.ai/">Claude</a> |
        <a href="https://www.bing.com/chat">Bing Chat</a></p>
        <p>Best regards,<br>
        MediaMind Team</p>
        <p><small>This is an automated reply. Please do not reply to
        this email.</small></p>
        """,
    )

    # Send the email (synchronously)
    EmailService.send_email(email)

    return {
        "message": f"Chat received and reply sent to {sender_email}.",
        "sender": chat.sender,
        "subject": chat.subject,
        "body": chat.body,
        "s3_key": chat.s3_key,
        "bucket": chat.bucket,
    }
