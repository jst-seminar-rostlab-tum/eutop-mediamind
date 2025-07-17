import asyncio
from io import BytesIO
from uuid import UUID

import markdown

from app.core.logger import get_logger
from app.services.chatbot_service.chatbot_context import ChatbotContext
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels

logger = get_logger(__name__)


class ChatbotResponse:
    @staticmethod
    async def create_prompt_from_context(
        email_conversation_id: UUID, subject: str, chat_body: str
    ) -> str:
        conversation_context = await ChatbotContext.load_conversation_context(
            email_conversation_id
        )
        prompt = f"""You are a professional customer support assistant for \
MediaMind, responding to user emails. Your tone must always be polite, \
empathetic, and solution-oriented. Your task is to provide a concise, \
professional, and helpful reply to the user's latest message. Find attached \
the PDF report related to the conversation, which contains relevant \
information that can help you answer the user's query.

Additionally, you can find the complete conversation history so far below. \
Messages are labelled as "user" (for user messages) and "assistant" \
(for your responses):

---
Subject: <{subject}>

{conversation_context}
---

The user's latest message is:
---
{chat_body}
---

Instructions:
- Respond only with the body of your reply, in clear and concise paragraphs.
- Include a salutation. In English, you should use 'Hi [username]'. Leave \
[username] in the salutation to be replaced with the user's first name.
- Include a closing statement. In English, you should use 'Best regards,
MediaMind Team'.
- Do not include subject lines.
- Do not repeat or quote the user's message.
- Do not use emojis or informal language.
- If the user's message is unclear, politely ask for clarification.
- If you do not know the answer, reply that to the user and politely ask for \
more context.
- Attached you will find the latest report in PDF format. Use it to \
provide accurate information.
- Focus on providing accurate, actionable, and relevant information to \
resolve the user's query.
- Always answer in the language of the user's last message."""
        return prompt

    @staticmethod
    async def generate(
        email_conversation_id: UUID,
        subject: str,
        chat_body: str,
        report_file: BytesIO,
    ) -> str:
        prompt = await ChatbotResponse.create_prompt_from_context(
            email_conversation_id=email_conversation_id,
            subject=subject,
            chat_body=chat_body,
        )

        llm_client = LLMClient(LLMModels.openai_4o_mini)
        try:
            llm_response = await asyncio.to_thread(
                llm_client.generate_response,
                prompt=prompt,
                file=report_file,
                temperature=0.7,
            )
        except Exception as e:
            logger.error(
                f"Error generating Chatbot response for email_conversation "
                f"with id={email_conversation_id} response: {str(e)}"
            )
            llm_response = f"""Thank you for your message regarding "\
{subject}". Unfortunately, we ran into a problem generating a response. \
Please try again later or contact us."""
        return llm_response

    @staticmethod
    def format(llm_response: str, user_first_name: str) -> str:
        llm_response_as_html = markdown.markdown(
            llm_response, extensions=["extra"]
        )

        email_as_html = llm_response_as_html.replace(
            "[username]", user_first_name
        )
        return email_as_html
