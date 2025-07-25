import asyncio
from io import BytesIO
from uuid import UUID

import markdown

from app.core.languages import Language
from app.core.logger import get_logger
from app.services.chatbot_service.chatbot_context import ChatbotContext
from app.services.email_service import EmailService
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import TaskModelMapping

logger = get_logger(__name__)


class ChatbotResponse:
    @staticmethod
    async def create_prompt_from_context(
        email_conversation_id: UUID,
        subject: str,
        chat_body: str,
        breaking_news: str,
    ) -> str:
        conversation_context = await ChatbotContext.load_conversation_context(
            email_conversation_id
        )
        prompt = f"""You are a professional customer support assistant for \
MediaMind, responding to user emails. Your tone must always be polite, \
empathetic, and solution-oriented. Your task is to provide a concise, \
professional, and helpful reply to the user's latest message. If available, \
you will find the PDF report attached, that is related to the conversation, \
and which contains relevant information that can help you answer the user's \
query. Otherwise, rely on the conversation context provided below to \
answer the user's query. You will always get the current breaking news \
for the last 24h. If related to the user's query, you can use it for your \
response. If the user wants more information regarding a breaking news item, \
you should also visit the URL attached to it and read the article, \
if possible. If the user asks about breaking news older than 24h, you should \
only use the context you have from the conversation history.

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

The current breaking news are:
---
{breaking_news}
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
- If available, you will find the latest report in PDF format attached. \
Use it to provide accurate information.
- Use the current breaking news only if the user asks about it. \
- Focus on providing accurate, actionable, and relevant information to \
resolve the user's query.
- Always answer in the language of the user's last message."""
        return prompt

    @staticmethod
    async def generate(
        email_conversation_id: UUID,
        subject: str,
        chat_body: str,
        report_file: BytesIO | None = None,
    ) -> str:
        breaking_news = ChatbotContext.load_breaking_news()
        prompt = await ChatbotResponse.create_prompt_from_context(
            email_conversation_id=email_conversation_id,
            subject=subject,
            chat_body=chat_body,
            breaking_news=breaking_news,
        )

        llm_client = LLMClient(TaskModelMapping.CHATBOT)
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
    def format(
        llm_response: str,
        user_first_name: str,
        user_language: str = Language.EN.value,
    ) -> str:
        llm_response_as_html = markdown.markdown(
            llm_response, extensions=["extra"]
        )

        email_as_html = llm_response_as_html.replace(
            "[username]", user_first_name
        )

        disclaimer_html = EmailService.get_disclaimer_html(user_language)
        email_as_html += disclaimer_html

        return email_as_html
