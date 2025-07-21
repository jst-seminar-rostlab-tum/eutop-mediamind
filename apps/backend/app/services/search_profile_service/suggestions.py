from typing import List

from fastapi import HTTPException

from app.core.languages import Language
from app.schemas.search_profile_schemas import (
    KeywordSuggestionResponse,
    KeywordSuggestionTopic,
)
from app.services.article_vector_service import ArticleVectorService
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import TaskModelMapping
from app.services.llm_service.prompts.keyword_suggestion_prompts import (
    KEYWORD_SUGGESTION_PROMPT_DE,
    KEYWORD_SUGGESTION_PROMPT_EN,
)


async def get_keyword_suggestions(
    search_profile_name: str,
    search_profile_language: str,
    related_topics: List[KeywordSuggestionTopic],
    selected_topic: KeywordSuggestionTopic,
) -> KeywordSuggestionResponse:
    """
    Generate keyword suggestions using LLM and validate via vector search.
    """
    # select prompt
    if search_profile_language == Language.DE.value:
        template = KEYWORD_SUGGESTION_PROMPT_DE
    elif search_profile_language == Language.EN.value:
        template = KEYWORD_SUGGESTION_PROMPT_EN
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language for keyword suggestions",
        )

    def _fmt(topics: List[KeywordSuggestionTopic]) -> str:
        if not topics:
            return "--"
        return "\n".join(
            f"{t.topic_name}: {', '.join(t.keywords)}" for t in topics
        )

    prompt = template.format(
        search_profile_name=search_profile_name,
        selected_topic_name=selected_topic.topic_name,
        selected_topic_keywords=", ".join(selected_topic.keywords),
        related_topics=_fmt(related_topics),
    )

    llm = LLMClient(TaskModelMapping.KEYWORD_SUGGESTION)
    try:
        response = llm.generate_typed_response(
            prompt, KeywordSuggestionResponse
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate keyword suggestions from LLM",
        )
    if not response or not response.suggestions:
        raise HTTPException(status_code=500, detail="Empty response from LLM")

    # validate suggestions
    avs = ArticleVectorService()
    scored = []
    for s in response.suggestions:
        try:
            docs = await avs.retrieve_by_similarity(
                query=s, score_threshold=0.5
            )
            scored.append((s, len(docs)))
        except Exception:
            raise HTTPException(
                status_code=502, detail="Vector search service unavailable"
            )
    scored.sort(key=lambda x: x[1], reverse=True)
    top5 = [s for s, _ in scored[:5]]
    return KeywordSuggestionResponse(suggestions=top5)
