from uuid import UUID

from app.core.config import configs
from app.core.logger import get_logger
from app.models.chat_message import MessageRole
from app.models.email import Email
from app.models.email_conversation import EmailConversation
from app.repositories.chatbot_repository import ChatbotRepository
from app.schemas.chatbot_schemas import ChatRequest
from app.schemas.user_schema import UserEntity
from app.services.email_service import EmailService
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels

logger = get_logger(__name__)


class ChatbotService:
    @staticmethod
    async def get_or_create_conversation(
        user: UserEntity, chat: ChatRequest
    ) -> EmailConversation:
        email_conversation = (
            await ChatbotRepository.get_conversation_by_email_and_subject(
                user.email, chat.subject
            )
        )
        if not email_conversation:
            email_conversation = await ChatbotRepository.create_conversation(
                user.email, chat.subject
            )
        return email_conversation

    @staticmethod
    async def load_conversation_context(
        email_conversation_id: UUID,
    ) -> str | None:
        conversation_history = (
            await ChatbotRepository.get_conversation_history(
                email_conversation_id
            )
        )
        context_messages = []
        for message in conversation_history:
            context_messages.append(f"{message.role.value}: {message.content}")

        conversation_context = (
            "\n\n".join(context_messages)
            if len(context_messages) > 0
            else None
        )
        return conversation_context

    @staticmethod
    async def create_prompt_from_context(
        email_conversation_id: UUID, chat_body: str
    ) -> str:
        conversation_context = await ChatbotService.load_conversation_context(
            email_conversation_id
        )
        print(f"Conversation context: {conversation_context}")
        prompt = f"""You are a professional customer support assistant for \
MediaMind, responding to user emails. Your tone must always be polite, \
empathetic, and solution-oriented. Your task is to provide a concise, \
professional, and helpful reply to the user's latest message.

Below is the complete conversation history so far. Messages are labelled as \
"user" (for user messages) and "assistant" (for your responses):

---
{conversation_context}
---

The user's latest message is:
---
{chat_body}
---

Instructions:
- Respond only with the body of your reply, in clear and concise paragraphs.
- Do not include greetings, salutations, subject lines, or closing statements.
- Do not repeat or quote the user's message.
- Do not use emojis or informal language.
- If the user's message is unclear, politely ask for clarification.
- If you do not know the answer, reply that to the user and politely ask for \
more context.
- Focus on providing accurate, actionable, and relevant information to \
resolve the user's query."""
        return prompt

    @staticmethod
    async def generate_llm_response(
        email_conversation_id: UUID, user_first_name: str, chat: ChatRequest
    ) -> str | None:
        prompt = await ChatbotService.create_prompt_from_context(
            email_conversation_id=email_conversation_id, chat_body=chat.body
        )
        print(f"Prompt for LLM: {prompt}")

        llm_client = LLMClient(LLMModels.openai_4o_mini)
        try:
            llm_response = llm_client.generate_response(
                prompt, temperature=0.7
            )
        except Exception as e:
            logger.error(f"Error generating Chatbot response: {str(e)}")
            llm_response = None
        return llm_response

    @staticmethod
    async def send_email_response(
        email_conversation_id, user_email: str, subject: str, content: str
    ):
        email = Email(
            sender=configs.SMTP_USER,
            recipient=user_email,
            subject=subject,
            content_type="text/HTML",
            content=content,
        )

        try:
            EmailService.send_ses_email(email)
            logger.info(
                f"Chat response sent to {user_email} for "
                f"email_conversation {email_conversation_id}"
            )
        except Exception as e:
            logger.error(f"Failed to send email to {user_email}: {str(e)}")
            raise e

    @staticmethod
    def format_llm_response(llm_response: str, user_first_name: str) -> str:
        llm_response_as_html = llm_response.replace("\n", "</p><p>")
        email_as_html = f"""<p>Hi {user_first_name},</p>
            <p>{llm_response_as_html}</p>
            <p>Best regards,<br>
            MediaMind Team</p>
            """
        return email_as_html

    @staticmethod
    async def store_chat_messages(
        email_conversation_id: UUID, chat_body: str, llm_response: str
    ):
        await ChatbotRepository.add_message(
            email_conversation_id=email_conversation_id,
            role=MessageRole.USER,
            content=chat_body,
        )
        await ChatbotRepository.add_message(
            email_conversation_id=email_conversation_id,
            role=MessageRole.ASSISTANT,
            content=llm_response,
        )

    @staticmethod
    async def generate_and_send_email_response(
        user: UserEntity, chat: ChatRequest
    ):
        email_conversation: EmailConversation = (
            await ChatbotService.get_or_create_conversation(user, chat)
        )
        llm_response = await ChatbotService.generate_llm_response(
            email_conversation_id=email_conversation.id,
            user_first_name=user.first_name,
            chat=chat,
        )
        llm_response = (
            llm_response
            or f"""\
Thank you for your message regarding "{chat.subject}". Unfortunately, we ran \
into a probelm generating a response. Please try again later or contact us."""
        )
        await ChatbotService.store_chat_messages(
            email_conversation.id, chat.body, llm_response
        )
        llm_response_as_html = ChatbotService.format_llm_response(
            llm_response, user.first_name
        )
        await ChatbotService.send_email_response(
            email_conversation_id=email_conversation.id,
            user_email=user.email,
            subject=chat.subject,
            content=llm_response_as_html,
        )
