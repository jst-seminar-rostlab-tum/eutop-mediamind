import re
from typing import Dict

from fastapi import APIRouter, Header, HTTPException

from app.core.config import configs
from app.schemas.chatbot_schemas import ChatRequest
from app.services.chatbot_service import ChatbotService
from app.services.user_service import UserService

router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)


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


@router.post("", response_model=Dict[str, str])
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

    try:
        await ChatbotService.generate_and_send_email_response(user, chat)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send chat response: {str(e)}",
        )
