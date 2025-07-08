# Refactored PDFService to use split modules
import uuid
from datetime import datetime, timedelta
from functools import partial
from io import BytesIO
from typing import Callable, List

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import AnchorFlowable

from app.core.logger import get_logger
from app.models.search_profile import SearchProfile
from app.repositories.article_repository import ArticleRepository
from app.repositories.entity_repository import ArticleEntityRepository
from app.services.translation_service import ArticleTranslationService

from ...repositories.search_profile_repository import SearchProfileRepository
from .colors import pdf_colors
from .fonts import register_fonts
from .news_item import NewsItem
from .styles import get_pdf_styles
from .utils import calculate_reading_time

logger = get_logger(__name__)


class PDFService:
    _fonts_registered = register_fonts()
    styles = get_pdf_styles(_fonts_registered)

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
        elif timeslot == "morning":
            match_start_time = match_stop_time - timedelta(hours=24)
        elif timeslot == "afternoon":
            match_start_time = match_stop_time - timedelta(hours=8)
        elif timeslot == "evening":
            match_start_time = match_stop_time - timedelta(hours=7)

        articles = await ArticleRepository.get_matched_articles_for_profile(
            search_profile_id
        )

        translator = ArticleTranslationService.get_translator(language)
        news_items = []
        for article in articles:
            entities = await ArticleEntityRepository.get_entities_by_article(
                article.id, language
            )
            persons = entities.get("person", [])
            organizations = entities.get("organization", [])
            industries = entities.get("industry", [])
            events = entities.get("event", [])
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
                content=(
                    getattr(article, f"content_{language}", None)
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
            search_profile, news_items, dimensions, translator
        )
        summaries_elements = PDFService.__create_summaries_elements(
            news_items, dimensions, translator
        )
        full_articles_elements = PDFService.__create_full_articles_elements(
            news_items, dimensions, translator
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

    @staticmethod
    def __draw_cover_elements(
        search_profile: SearchProfile,
        news_items: List[NewsItem],
        dimensions: tuple[float, float],
        translator: Callable[[str], str],
    ) -> List["Flowable"]:
        width, height = dimensions
        # TOC entry style
        toc_entry_style = ParagraphStyle(
            name="TOCEntry",
            fontName="DVS-Bold",
            fontSize=10,
            textColor=pdf_colors["blue"],
            spaceAfter=0,
            bulletIndent=0,
            leftIndent=0,
            leading=14,
            alignment=TA_JUSTIFY,
        )

        metadata_style = ParagraphStyle(
            name="HeaderTitle",
            fontName="DVS",
            fontSize=10,
            textColor=pdf_colors["darkGrey"],
            spaceAfter=6,
            bulletIndent=0,
            leftIndent=6,
            leading=10,
            alignment=TA_JUSTIFY,
        )

        story = []
        # Title
        story.append(
            Paragraph(
                f"<b> \
                   <font size=36>{translator('Daily News Report')}</font>\
                </b>",
                PDFService.styles["title_style"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        now = datetime.today()
        month = now.strftime("%B")
        now_str = (
            f"{now.strftime('%d')} {translator(month)} {now.strftime('%Y')} – "
            f"{now.strftime('%H:%M')}"
        )
        # Subtitle with current date and time
        story.append(
            Paragraph(
                f"<b><font size=16>{now_str}</font></b>",
                PDFService.styles["title_style"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        # Total reading time
        total_text = " ".join(news.content for news in news_items)
        total_minutes = calculate_reading_time(
            total_text, words_per_minute=180
        )

        # Total reading time (compact Flowable)
        class EstimatedReadingTimeFlowable(Flowable):
            def __init__(self, estimated_minutes):
                super().__init__()
                self.estimated_minutes = estimated_minutes

            def wrap(self, available_width, available_height):
                return available_width, 16

            def draw(self):
                canvas = self.canv
                canvas.setFont("DVS", 12)
                canvas.setFillColor(pdf_colors["darkgreen"])
                label = translator("Estimated Reading Time") + ": "
                canvas.drawString(0, 0, label)
                label_width = canvas.stringWidth(label, "DVS", 12)
                canvas.setFont("DVS-Bold", 12)
                canvas.drawString(label_width, 0, str(self.estimated_minutes))
                label_width += canvas.stringWidth(
                    str(self.estimated_minutes), "DVS-Bold", 12
                )
                canvas.drawString(label_width, 0, f" {translator('min')}")

        story.append(EstimatedReadingTimeFlowable(total_minutes))
        story.append(Spacer(1, 0.3 * inch))

        # Add spacing before TOC
        story.append(Spacer(1, 12))

        # TOC Title (bold, styled)
        story.append(
            Paragraph(
                translator("Table of Contents"),
                ParagraphStyle(
                    name="TOCHeader",
                    fontName="DVS-Bold",
                    fontSize=16,
                    spaceAfter=12,
                    textColor=pdf_colors["blue"],
                ),
            )
        )
        # Horizontal rule before TOC
        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=pdf_colors["gray"],
                spaceBefore=6,
                spaceAfter=6,
            )
        )

        # TOC entries
        for i, news in enumerate(news_items):
            # Add anchor for TOC entry (optional, if needed)
            story.append(AnchorFlowable(f"toc_entry_{i}"))
            story.append(
                Paragraph(
                    f'<a href="#toc_summary_{i}">{i+1}. {news.title}</a><br/>',
                    toc_entry_style,
                )
            )
            meta_para = Paragraph(
                f"""
                <para>
                <font size="9">{news.newspaper.name}</font><br/>
                <font size="9">{news.published_at}</font>
                </para>
                """,
                metadata_style,
            )

            summary_link = (
                f'<a href="#toc_summary_{i}">'
                f'&nbsp;{translator("Summary")}&nbsp;'
                "</a>"
            )
            full_article_link = (
                f'<a href="#toc_article_{i}">'
                f'&nbsp;{translator("Full Article")}&nbsp;'
                "</a>"
            )
            button_para = Paragraph(
                f"""
                <font backColor="{pdf_colors["lightgrey"]}" size="9">
                    {summary_link}
                </font>
                &nbsp;&nbsp;
                <font backColor="{pdf_colors["lightgrey"]}" size="9">
                    {full_article_link}
                </font>
                """,
                PDFService.styles["button_style"],
            )

            row = [[meta_para, button_para]]
            table = Table(
                row, colWidths=[4 * inch, 2 * inch]
            )  # 4 and 2 are the column widths
            table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )

            story.append(table)

            story.append(Spacer(1, 12))

        # Horizontal rule after TOC
        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=pdf_colors["gray"],
                spaceBefore=6,
                spaceAfter=6,
            )
        )
        # Add spacing after TOC
        story.append(Spacer(1, 12))
        return story

    @staticmethod
    def draw_header_footer(canvas, doc, translator):
        canvas.saveState()
        width, height = A4

        style = ParagraphStyle(
            name="HeaderTitle",
            fontName="DVS-BoldOblique",
            fontSize=10,
            textColor=pdf_colors["main"],
            leading=12,
        )

        now = datetime.today()
        month = now.strftime("%B")
        now_str = (
            f"{now.strftime('%d')} {translator(month)} {now.strftime('%Y')} – "
            f"{now.strftime('%H:%M')}"
        )
        data = [
            [
                Paragraph(f"<b>{translator('Daily News Report')}</b>", style),
                Paragraph(f"<b>{now_str}</b>", style),
            ]
        ]
        # 4.5 is the width of the first column, 4 is the second
        table = Table(data, colWidths=[4.25 * inch, 4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                ]
            )
        )
        table.wrapOn(canvas, width, height)
        table.drawOn(canvas, inch, height - inch + 20)

        # --- Draw page number in footer ---
        canvas.setFont("DVS", 10)
        canvas.setFillColor(pdf_colors["main"])
        page_str = translator("Page") + f" {doc.page}"
        canvas.drawRightString(width - inch, 0.4 * inch, page_str)

        canvas.restoreState()

    @staticmethod
    def __create_summaries_elements(
        news_items: List[NewsItem],
        dimensions: tuple[float, float],
        translator: Callable[[str], str],
    ) -> List["Flowable"]:
        width, height = dimensions  # TODO
        story = []
        for i, news in enumerate(news_items):
            story.append(AnchorFlowable(f"toc_summary_{i}"))
            story.append(
                Paragraph(
                    str(i + 1) + ". " + news.title or "",
                    PDFService.styles["newspaper_style"],
                )
            )
            story.append(Spacer(1, 0.05 * inch))
            story.append(
                Paragraph(
                    f'<link href="{news.url}">{news.newspaper.name}</link>'
                    or "",
                    PDFService.styles["keywords_style"],
                )
            )
            story.append(
                Paragraph(news.published_at, PDFService.styles["date_style"])
            )
            story.append(Spacer(1, 0.05 * inch))
            summary_text = news.summary.replace("\n", "<br/>")
            # Add the summary paragraph directly instead of in a Table
            story.append(
                Paragraph(summary_text, PDFService.styles["summary_style"])
            )
            story.append(Spacer(1, 0.05 * inch))
            dest_name = f"full_{news.id}"
            story.append(
                Paragraph(
                    f"<a href='#{dest_name}'>"
                    f"{translator('Read full article')}</a>",
                    PDFService.styles["link_style"],
                )
            )
            if i != len(news_items) - 1:
                story.append(
                    HRFlowable(
                        width="100%", thickness=1, color=pdf_colors["main"]
                    )
                )
                story.append(Spacer(1, 0.1 * inch))
        return story

    @staticmethod
    def __create_full_articles_elements(
        news_items: List[NewsItem],
        dimensions: tuple[float, float],
        translator: Callable[[str], str],
    ) -> List["Flowable"]:
        story = []
        for i, news in enumerate(news_items):
            dest_name = f"full_{news.id}"
            story.append(AnchorFlowable(dest_name))
            story.append(AnchorFlowable(f"toc_article_{i}"))
            story.append(
                Paragraph(
                    str(i + 1) + ". " + news.title,
                    PDFService.styles["title_style"],
                )
            )

            # Wrap metadata in a styled table box
            metadata_text = f"""
            {translator('Published at')}: {news.published_at} |
             {translator('Newspaper')}: {news.newspaper.name}
                    """
            metadata_para = Paragraph(
                metadata_text, PDFService.styles["metadata_style"]
            )
            metadata_first = Table(
                [[metadata_para]],
                colWidths=[dimensions[0] - 2 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), pdf_colors["white"]),
                        ("BOX", (0, 0), (-1, -1), 0.25, pdf_colors["white"]),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ]
                ),
            )
            story.append(metadata_first)

            # Summary
            story.append(
                Paragraph(
                    translator("Summary"),
                    PDFService.styles["subtitle_style"],
                )
            )
            story.append(
                Paragraph(news.summary, PDFService.styles["content_style"])
            )
            story.append(Spacer(1, 0.15 * inch))

            story.append(
                Paragraph(
                    translator("Article Content"),
                    PDFService.styles["subtitle_style"],
                )
            )

            # Calculate reading time
            reading_time = calculate_reading_time(news.content)
            reading_time_text = (
                f"{translator('Estimated Reading Time')}: "
                f"{reading_time} {translator('min')}"
            )
            reading_time_para = Paragraph(
                reading_time_text, PDFService.styles["link_style"]
            )
            read_summary_para = Paragraph(
                f"""
                <para alignment=\"right\">
                    <a href=\"#toc_summary_{i}\">\n
                    <u><font>{translator('Back to Summary List')}</font></u>\n
                    </a>
                </para>
                """,
                PDFService.styles["link_style"],
            )
            # Put reading time and read summary in a box
            reading_time_box = Table(
                [[reading_time_para, read_summary_para]],
                colWidths=[
                    2.5 * inch,
                    (dimensions[0] - 2 * inch - 2.5 * inch),
                ],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), pdf_colors["white"]),
                        ("BOX", (0, 0), (-1, -1), 0.25, pdf_colors["white"]),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                ),
            )
            story.append(reading_time_box)

            # Content
            content_text = news.content.replace("\n", "<br/>")
            story.append(
                Paragraph(content_text, PDFService.styles["content_style"])
            )
            story.append(Spacer(1, 0.3 * inch))

            # Metadata Box
            word_count = len(news.content.split()) if news.content else 0
            persons_str = ", ".join(f"{p}" for p in news.persons)
            organizations_str = ", ".join(f"{i}" for i in news.organizations)
            industries_str = ", ".join(f"{i}" for i in news.industries)
            events_str = ", ".join(f"{i}" for i in news.events)

            # Prepare metadata as label-value pairs for two columns
            metadata_rows = [
                [
                    Paragraph(
                        f"{translator('Words')}:",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        str(word_count), PDFService.styles["metadata_style"]
                    ),
                ],
                [
                    Paragraph(
                        f"{translator('Reading Time')}:",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        f"{reading_time} {translator('min')}",
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        f"{translator('Author')}:",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        news.author, PDFService.styles["metadata_style"]
                    ),
                ],
                [
                    Paragraph(
                        f"{translator('Newspaper')}:",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        news.newspaper.name,
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        f"<b>{translator('Published at')}:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        news.published_at, PDFService.styles["metadata_style"]
                    ),
                ],
                [
                    Paragraph(
                        f"<b>{translator('Language')}:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        news.language or translator("Unknown"),
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        f"<b>{translator('Category')}:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        news.category or translator("Unknown"),
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        f"<b>{translator('Keywords')}:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        (
                            ", ".join(news.keywords)
                            if news.keywords
                            else translator("None")
                        ),
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        f"<b>{translator('Mentioned in this article')}:</b>",
                        PDFService.styles["metadata_subtitle_style"],
                    ),
                    "",
                ],
                [
                    Paragraph(
                        f"<b>{translator('People')}:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        persons_str if persons_str else translator("None"),
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        f"<b>{translator('Organizations')}:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        (
                            organizations_str
                            if organizations_str
                            else translator("None")
                        ),
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        f"<b>{translator('Industries')}:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        (
                            industries_str
                            if industries_str
                            else translator("None")
                        ),
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        f"<b>{translator('Events')}:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        events_str if events_str else translator("None"),
                        PDFService.styles["metadata_style"],
                    ),
                ],
            ]

            combined_box = Table(
                metadata_rows,
                colWidths=[
                    (dimensions[0] - 4 * inch) * 0.25,
                    (dimensions[0] - 1.5 * inch) * 0.75,
                ],
                style=TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            pdf_colors["whitesmoke"],
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.25,
                            pdf_colors["lightgrey"],
                        ),
                        ("LEFTPADDING", (0, 0), (-1, -1), 2),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 2),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                        (
                            "SPAN",
                            (0, 8),
                            (1, 8),
                        ),  # Span both columns for "Mentioned in this article"
                    ]
                ),
            )
            story.append(combined_box)
            story.append(Spacer(1, 0.1 * inch))

            # URL Link Button
            link_img = Image("assets/link_icon.png", width=16, height=16)
            button = Table(
                [
                    [
                        link_img,
                        Paragraph(
                            f'<a href="{news.url}">'
                            f'<b>{translator("Read Article at Newspaper")}'
                            f"</b></a>",
                            PDFService.styles["link_style"],
                        ),
                    ]
                ],
                colWidths=[0.2 * inch, 2.1 * inch],
                hAlign="RIGHT",
            )
            button.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), pdf_colors["white"]),
                        ("TEXTCOLOR", (0, 0), (-1, -1), pdf_colors["blue"]),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        (
                            "INNERGRID",
                            (0, 0),
                            (-1, -1),
                            0,
                            pdf_colors["white"],
                        ),
                        ("BOX", (0, 0), (-1, -1), 1, pdf_colors["white"]),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ]
                )
            )
            story.append(button)

            if i != len(news_items) - 1:
                story.append(PageBreak())
        return story
