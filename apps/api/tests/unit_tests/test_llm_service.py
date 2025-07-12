import pytest

from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels


@pytest.fixture
def llm_service_wrong_key():
    return LLMClient(model=LLMModels.openai_4o)
