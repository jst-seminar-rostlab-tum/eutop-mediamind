import uuid
from typing import Optional

from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI

from app.core.config import configs
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository


class ArticleSummaryService:
    @staticmethod
    def summarize_text(text: str) -> str:
        """
        Summarizes the given text using a language model.

        Args:
            text (str): The text to summarize.

        Returns:
            str: The summarized text.
        """
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=configs.OPENAI_API_KEY,
        )

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_text(text)
        docs = [Document(page_content=t) for t in texts]

        chain = load_summarize_chain(llm, chain_type="map_reduce")
        summary = chain.invoke(docs)
        return summary["output_text"]

    @staticmethod
    async def summarize_and_store(article_id: uuid.UUID) -> Optional[Article]:
        """
        Fetches an Article by ID, generates a summary for its content,
        and updates only the `summary` field in the database.

        Returns:
            The updated Article if it exists, otherwise None.
        """
        article = await ArticleRepository.get_article_by_id(article_id)

        if not article:
            return None

        summary = ArticleSummaryService.summarize_text(article.content)
        return await ArticleRepository.update_summary(article_id, summary)
