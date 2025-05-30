import uuid
from typing import Optional

from langchain.text_splitter import CharacterTextSplitter

from app.models.article import Article
from app.repositories.article_repository import ArticleRepository
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels


def summarize_text(text: str) -> str:
    """
    Summarizes the given text using LLMClient.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summarized text.
    """
    llm_client = LLMClient(model=LLMModels.openai_4o_mini)

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_text(text)

    # Summarize each chunk
    partial_summaries = []
    for chunk in chunks:
        summary = llm_client.generate_response(
            f"Summarize the following:\n\n{chunk}"
        )
        partial_summaries.append(summary)

    # Combine partial summaries into a final summary
    combined_text = "\n".join(partial_summaries)
    final_summary = llm_client.generate_response(
        f"Summarize the following:\n\n{combined_text}"
    )

    return final_summary


def summarize_and_store(article_id: uuid.UUID) -> Optional[Article]:
    """
    Summarizes an article's content and stores the result.

    Args:
        article_id (uuid.UUID): ID of the article to summarize.

    Returns:
        Optional[Article]: The updated article or None if not found.
    """
    article = ArticleRepository.get_article_by_id(article_id)

    if not article:
        return None

    summary = summarize_text(article.__getattribute__("content"))
    article.summary = summary

    return ArticleRepository.update_article(article)
