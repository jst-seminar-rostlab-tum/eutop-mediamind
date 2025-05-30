from unittest.mock import patch

import litellm.exceptions
import pytest

from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels


@pytest.fixture
def llm_service_wrong_key():
    return LLMClient(model=LLMModels.openai_4o)


@patch("app.services.llm_service.llm_client.completion")
def test_generate_response_with_wrong_api_key(
    mock_completion, llm_service_wrong_key
):
    mock_completion.side_effect = litellm.exceptions.AuthenticationError(
        message="Invalid API key", llm_provider="openai", model="gpt-4o"
    )

    # Test that the error is propagated
    with pytest.raises(litellm.exceptions.AuthenticationError):
        llm_service_wrong_key.generate_response("Hello!")