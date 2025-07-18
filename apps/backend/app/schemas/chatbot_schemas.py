from pydantic import BaseModel


class ChatRequest(BaseModel):
    sender: str
    subject: str
    body: str
