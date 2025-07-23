# flake8: noqa: E501
# Refactored PDFService to use split modules
import uuid
from functools import partial
from io import BytesIO
from typing import Callable, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
)

from app.core.logger import get_logger
from app.models.entity import EntityType
from app.repositories.article_repository import ArticleRepository
from app.repositories.entity_repository import ArticleEntityRepository
from app.services.translation_service import ArticleTranslationService

# Connect the external functions as a static methods of PDFService
from .colors import pdf_colors
from .cover_elements import draw_cover_elements as _draw_cover_elements
from .fonts import register_fonts
from .full_articles_elements import create_full_articles_elements
from .header_footer import draw_header_footer as _draw_header_footer
from .news_item import NewsItem
from .original_elements import create_original_articles_elements
from .styles import get_pdf_styles
from .summaries_elements import create_summaries_elements

# Hyphenation utilities
from .utils import hyphenate_text

logger = get_logger("PDF_SERVICE")


class PDFService:
    @staticmethod
    def _draw_cover_elements(news_items, dimensions, translator):
        return _draw_cover_elements(
            news_items, dimensions, PDFService.styles, translator
        )

    @staticmethod
    def draw_header_footer(*args, **kwargs):
        return _draw_header_footer(*args, **kwargs)

    @staticmethod
    def _create_summaries_elements(news_items, dimensions, translator):
        return create_summaries_elements(
            news_items, dimensions, translator, PDFService.styles, pdf_colors
        )

    @staticmethod
    def _create_full_articles_elements(*args, **kwargs):
        return create_full_articles_elements(*args, **kwargs)

    @staticmethod
    def _create_original_elements(news_items, styles, translator):
        return create_original_articles_elements(
            news_items, styles, translator
        )

    # Loading Our custom fonts
    styles = get_pdf_styles(register_fonts())

    @staticmethod
    async def create_pdf(
        search_profile_id: uuid.UUID,
        timeslot: str,
        language: str,
    ) -> tuple[bytes, bool]:
        try:
            logger.info(
                f"Starting PDF generation for profile={search_profile_id}, timeslot={timeslot}, language={language}"
            )
            # Obtain translator for the specified language
            if timeslot not in ["morning", "afternoon", "evening"]:
                logger.error(
                    "Invalid timeslot. Must be one of: ['morning', 'afternoon',"
                    " 'evening']"
                )

            articles = await ArticleRepository.get_matched_articles_for_profile_for_create_pdf(
                search_profile_id
            )

            empty_pdf = False
            if not articles:
                logger.info(
                    f"No articles found for profile={search_profile_id}, timeslot={timeslot}, language={language}. Generating empty PDF."
                )
                empty_pdf = True

            translator = ArticleTranslationService.get_translator(language)
            news_items = []
            for article in articles:
                try:
                    entities = (
                        await ArticleEntityRepository.get_entities_by_article(
                            article.id, language
                        )
                    )
                    persons = entities.get(EntityType.PERSON.value, [])
                    organizations = entities.get(
                        EntityType.ORGANIZATION.value, []
                    )
                    industries = entities.get(EntityType.INDUSTRY.value, [])
                    events = entities.get(EntityType.EVENT.value, [])
                    citations = entities.get(EntityType.CITATION.value, [])
                    if article.published_at:
                        published_at_raw = article.published_at
                        month = published_at_raw.strftime("%B")
                        published_at_str = (
                            f"{published_at_raw.strftime('%d')} "
                            f"{translator(month)} {published_at_raw.strftime('%Y')} "
                            f"– {published_at_raw.strftime('%H:%M')}"
                        )
                    else:
                        published_at_str = None
                    missing_sub_message = (
                        translator("This content is only available to")
                        + f" {article.subscription.name} "
                        + translator("subscribers")
                        + "."
                    )
                    # Only hyphenate the summary
                    content = getattr(
                        article, f"content_{language}", None
                    ) or (
                        missing_sub_message
                        if article.content == ""
                        else article.content
                    )
                    content_original = getattr(
                        article, "content_original", None
                    ) or (
                        missing_sub_message
                        if article.content == ""
                        else article.content
                    )
                    summary = getattr(
                        article, f"summary_{language}", None
                    ) or (
                        article.summary
                        if article.summary
                        else translator("No summary available") + "."
                    )
                    summary = hyphenate_text(summary, language)
                    news_item = NewsItem(
                        id=article.id,
                        title=(
                            getattr(article, f"title_{language}", None)
                            or article.title
                        ),
                        title_original=(
                            getattr(article, "title_original", None)
                            or article.title
                        ),
                        content=content,
                        content_original=content_original,
                        url=article.url,
                        author=(
                            ", ".join(article.authors)
                            if article.authors
                            else translator("Unknown")
                        ),
                        image_url=(
                            article.image_url
                            if hasattr(article, "image_url")
                            else None
                        ),
                        published_at=published_at_str,
                        language=(
                            article.language if article.language else None
                        ),
                        summary=summary,
                        subscription_id=article.subscription.id,
                        newspaper=article.subscription
                        or translator("Unknown"),
                        # Category: join topic_name and score as 'Topic: XX.XX%'
                        category=(
                            ", ".join(
                                f"{topic.get('topic_name', '')}: {round(topic.get('score', 0)*100, 2):.2f}%"
                                for topic in getattr(
                                    article, "topics_data", []
                                )
                                if topic.get("topic_name")
                            )
                            if hasattr(article, "topics_data")
                            and article.topics_data
                            else None
                        ),
                        # Keywords: join keyword_name and score as 'keyword: XX.XX%'
                        keywords=(
                            [
                                f"{keyword.get('keyword_name', '')}: {round(keyword.get('score', 0)*100, 2):.2f}%"
                                for topic in getattr(
                                    article, "topics_data", []
                                )
                                for keyword in topic.get("keywords", [])
                                if keyword.get("keyword_name")
                            ]
                            if hasattr(article, "topics_data")
                            and article.topics_data
                            else []
                        ),
                        persons=persons,
                        organizations=organizations,
                        industries=industries,
                        events=events,
                        citations=citations,
                    )
                    news_items.append(news_item)
                except Exception as e:
                    logger.error(
                        f"Error processing article {getattr(article, 'id', 'unknown')}: {e}"
                    )
                    continue
            logger.info(f"Collected {len(news_items)} news items for PDF.")
            return PDFService.draw_pdf(news_items, translator), empty_pdf
        except Exception as e:
            logger.error(f"Error in create_pdf: {e}")
            # Return empty PDF bytes and True to indicate empty
            return b"", True

    @staticmethod
    def draw_pdf(
        news_items: List[NewsItem],
        translator: Callable[[str], str],
    ) -> bytes:
        try:
            dimensions = A4
            logger.debug("Articles chosen before PDF Generation:")
            # Logging which articles, if they have summaries and keywords
            for news in news_items:
                logger.debug(
                    f"""Processing News item: {news.id}, Summary:\
                    {True if news.summary else False}, Keywords:\
                    {True if news.keywords else 'False'}
                    """
                )

            try:
                logger.info("Building cover page elements.")
                cover_elements = PDFService._draw_cover_elements(
                    news_items, dimensions, translator
                )
            except Exception as e:
                logger.error(f"Error building cover page elements: {e}")
                cover_elements = []

            try:
                logger.info("Building summaries section elements.")
                summaries_elements = PDFService._create_summaries_elements(
                    news_items, dimensions, translator
                )
            except Exception as e:
                logger.error(f"Error building summaries section elements: {e}")
                summaries_elements = []

            try:
                logger.info("Building full articles section elements.")
                full_articles_elements = (
                    PDFService._create_full_articles_elements(
                        news_items, dimensions, translator, PDFService.styles
                    )
                )
            except Exception as e:
                logger.error(
                    f"Error building full articles section elements: {e}"
                )
                full_articles_elements = []

            try:
                logger.info("Building appendix with original articles.")
                original_elements = PDFService._create_original_elements(
                    news_items, PDFService.styles, translator
                )
            except Exception as e:
                logger.error(
                    f"Error building appendix with original articles: {e}"
                )
                original_elements = []

            # Combine all elements
            all_elements = []
            all_elements.append(NextPageTemplate("Cover"))
            all_elements.extend(cover_elements)
            # Add NextPageTemplate to switch to three-column layout for summaries
            all_elements.append(NextPageTemplate("SummariesThreeCol"))
            all_elements.append(PageBreak())
            all_elements.extend(summaries_elements)
            # Switch back to full-width single-column layout for full articles
            all_elements.append(NextPageTemplate("FullArticles"))
            all_elements.append(PageBreak())
            all_elements.extend(full_articles_elements)
            # Add appendix with original articles
            all_elements.extend(original_elements)

            buffer = BytesIO()
            width, height = dimensions
            margin = 1.5 * cm

            # Use a single frame for simplicity, as elements can use PageBreaks
            frame = Frame(
                margin,
                margin,
                width - 2 * margin,
                height - 2 * margin,
                id="main",
            )

            # Define a full-width frame for full articles
            full_article_frame = Frame(
                margin,
                margin,
                width - 2 * margin,
                height - 2.5 * margin,
                id="full_article",
            )

            # Define three vertical frames evenly spaced across the page width for
            # summaries
            frame_width = (width - 2 * margin) / 3
            frames = [
                Frame(
                    margin + i * frame_width,
                    margin,
                    frame_width,
                    height - 2 * margin,
                    id=f"col{i}",
                )
                for i in range(3)
            ]

            doc = BaseDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=margin,
                leftMargin=margin,
                topMargin=margin,
                bottomMargin=margin,
            )

            on_page = partial(
                PDFService.draw_header_footer, translator=translator
            )
            doc.addPageTemplates(
                [
                    PageTemplate(id="Cover", frames=[frame]),
                    PageTemplate(
                        id="SummariesThreeCol",
                        frames=frames,
                        onPage=on_page,
                    ),
                    PageTemplate(
                        id="FullArticles",
                        frames=[full_article_frame],
                        onPage=on_page,
                    ),
                ]
            )
            try:
                doc.build(all_elements)
            except Exception as e:
                logger.error(f"Error building PDF document: {e}")
                # Return empty PDF if build fails
                return b""
            buffer.seek(0)
            logger.info("PDF generation complete and ready for upload.")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return b""
