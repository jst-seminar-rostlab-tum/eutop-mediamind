from litellm import completion

from app.core.config import configs
from app.core.logger import get_logger
from app.services.llm_service.llm_models import LLMModels

logger = get_logger(__name__)


class LLMClient:
    """
    This takes the LiteLLM Gateway to communicate to any LLM provider

    Parameters:
        model (LLMModels): An enum value representing the language model to
        use. Extend it if you need it
        api_key (Optional[str]): API key for authentication. If None, assumes
        that environment variable is set accordingly
        https://docs.litellm.ai/docs/

    Examples:
        >>> service = LLMClient(LLMModels.GPT_4)
        >>> response = service.generate_response("Tell me a joke")
    """

    def __init__(self, model: LLMModels):
        self.model = model.value
        self.api_key = configs.OPENAI_API_KEY

    def generate_response(self, prompt: str) -> str:
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        if self.api_key:
            kwargs["api_key"] = self.api_key

        try:
            response = completion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.exception(
                f"Error occurred while generating response with model \
                '{self.model}': {e}"
            )
            raise
