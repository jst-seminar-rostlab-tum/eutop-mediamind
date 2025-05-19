from typing import Optional

from litellm import completion

from app.services.llm_service.llm_models import LLMModels


class LLMClient:
    """
    This takes the LiteLLM Gateway to communicate to any llm provider

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

    def __init__(self, model: LLMModels, api_key: Optional[str] = None):
        self.model = model.value
        self.api_key = api_key

    def generate_response(self, prompt: str) -> str:
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        if self.api_key:
            kwargs["api_key"] = self.api_key

        response = completion(**kwargs)
        return response.choices[0].message.content
