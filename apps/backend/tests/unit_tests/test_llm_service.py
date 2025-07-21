import pytest

from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import TaskModelMapping


@pytest.fixture
def llm_service_wrong_key():
    return LLMClient(model=TaskModelMapping.TEST)
