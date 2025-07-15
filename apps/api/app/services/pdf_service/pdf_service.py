# Refactored PDFService to use split modules
import uuid
from datetime import datetime
from functools import partial
from io import BytesIO
from typing import Callable, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
)

from app.core.logger import get_logger
from app.models.entity import EntityType
from app.models.search_profile import SearchProfile
from app.repositories.article_repository import ArticleRepository
from app.repositories.entity_repository import ArticleEntityRepository
from app.services.translation_service import ArticleTranslationService

# PDFService uses split modules
from ...repositories.search_profile_repository import SearchProfileRepository
from .colors import pdf_colors

# Connect the external functions as a static methods of PDFService
from .cover_elements import draw_cover_elements as _draw_cover_elements
from .fonts import register_fonts
from .full_articles_elements import create_full_articles_elements
from .header_footer import draw_header_footer as _draw_header_footer
from .news_item import NewsItem
from .original_elements import create_original_articles_elements
from .styles import get_pdf_styles
from .summaries_elements import create_summaries_elements

logger = get_logger(__name__)


class PDFService:
    # Loading Our custom fonts
    styles = get_pdf_styles(register_fonts())

    @staticmethod
    async def create_pdf(
        search_profile_id: uuid.UUID,
        timeslot: str,
        language: str,
        match_stop_time: datetime,
    ) -> bytes:
        # Obtain translator for the specified language
        if timeslot not in ["morning", "afternoon", "evening"]:
            logger.info(
                "Invalid timeslot. Must be one of: ['morning', 'afternoon',"
                " 'evening']"
            )

        articles = await ArticleRepository.get_matched_articles_for_profile(
            search_profile_id
        )

        translator = ArticleTranslationService.get_translator(language)
        news_items = []
        for article in articles:
            entities = await ArticleEntityRepository.get_entities_by_article(
                article.id, language
            )
            persons = entities.get(EntityType.PERSON.value, [])
            organizations = entities.get(EntityType.ORGANIZATION.value, [])
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
            news_item = NewsItem(
                id=article.id,
                title=(
                    getattr(article, f"title_{language}", None)
                    or article.title
                ),
                title_original=(
                    getattr(article, "title_original", None) or article.title
                ),
                content=(
                    getattr(article, f"content_{language}", None)
                    or article.content
                ),
                content_original=(
                    getattr(article, "content_original", None)
                    or article.content
                ),
                url=article.url,
                author=(
                    ", ".join(article.authors)
                    if article.authors
                    else translator("Unknown")
                ),
                published_at=published_at_str,
                language=article.language if article.language else None,
                category=(
                    ", ".join(article.categories)
                    if article.categories
                    else None
                ),
                summary=(
                    getattr(article, f"summary_{language}", None)
                    or (
                        article.summary
                        if article.summary
                        else translator("No summary available") + "."
                    )
                ),
                subscription_id=article.subscription.id,
                newspaper=article.subscription or translator("Unknown"),
                keywords=[keyword.name for keyword in article.keywords],
                image_url=None,
                persons=persons,
                organizations=organizations,
                industries=industries,
                events=events,
                citations=citations,
            )
            news_items.append(news_item)
        search_profile = (
            await SearchProfileRepository.get_search_profile_by_id(
                search_profile_id
            )
        )
        return PDFService.draw_pdf(search_profile, news_items, translator)

    @staticmethod
    def draw_pdf(
        search_profile: SearchProfile,
        news_items: List[NewsItem],
        translator: Callable[[str], str],
    ) -> bytes:
        dimensions = A4
        logger.debug("Articles chosen before PDF Generation:")
        # Logging which articles, if they have summaries and keywords
        for news in news_items:
            logger.debug(
                f"Processing News item: {news.id}, Summary:  \
                {True if news.summary else False}, Keywords:  \
                {True if news.keywords else 'False'}"
            )

        # Prepare all flowable elements for the PDF
        cover_elements = PDFService.__draw_cover_elements(
            news_items, dimensions, translator
        )
        summaries_elements = PDFService.__create_summaries_elements(
            news_items, dimensions, translator
        )
        full_articles_elements = PDFService.__create_full_articles_elements(
            news_items, dimensions, translator, PDFService.styles
        )
        # Add appendix with original articles
        original_elements = PDFService._PDFService__create_original_elements(
            news_items, PDFService.styles, translator
        )
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
        margin = inch

        # Use a single frame for simplicity, as elements can use PageBreaks
        frame = Frame(
            margin, margin, width - 2 * margin, height - 2 * margin, id="main"
        )

        # Define a full-width frame for full articles
        full_article_frame = Frame(
            margin,
            margin,
            width - 2 * margin,
            height - 2 * margin,
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
        on_page = partial(PDFService.draw_header_footer, translator=translator)
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
        doc.build(all_elements)
        buffer.seek(0)
        return buffer.getvalue()


PDFService._PDFService__draw_cover_elements = staticmethod(
    lambda news_items, dimensions, translator: _draw_cover_elements(
        news_items, dimensions, PDFService.styles, translator
    )
)

PDFService.draw_header_footer = staticmethod(_draw_header_footer)

PDFService._PDFService__create_summaries_elements = staticmethod(
    lambda news_items, dimensions, translator: create_summaries_elements(
        news_items, dimensions, translator, PDFService.styles, pdf_colors
    )
)

PDFService._PDFService__create_full_articles_elements = staticmethod(
    create_full_articles_elements
)

PDFService._PDFService__create_original_elements = staticmethod(
    lambda news_items, styles, translator: create_original_articles_elements(
        news_items, styles, translator
    )
)
