# Refactored PDFService to use split modules
import json
import os
import random
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import List

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

from ...repositories.search_profile_repository import SearchProfileRepository
from .colors import pdf_colors
from .fonts import register_fonts
from .news_item import NewsItem
from .styles import get_pdf_styles
from .utils import calculate_reading_time

logger = get_logger(__name__)

# Load metadata for politicians, companies, people, industries, legislations
with open(
    os.path.join(os.path.dirname(__file__), "../../../assets/metadata.json"),
    "r",
    encoding="utf-8",
) as f:
    METADATA = json.load(f)


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
        if timeslot not in ["morning", "afternoon", "evening"]:
            logger.info(
                "Invalid timeslot. Must be one of: ['morning', 'afternoon',"
                " 'evening']"
            )
        elif timeslot == "morning":
            match_start_time = match_stop_time - timedelta(hours=700)
        elif timeslot == "afternoon":
            match_start_time = match_stop_time - timedelta(hours=8)
        elif timeslot == "evening":
            match_start_time = match_stop_time - timedelta(hours=7)

        articles = await ArticleRepository.get_matched_articles_for_profile(
            search_profile_id, match_start_time, match_stop_time
        )

        news_items = []
        for article in articles:
            politicians = random.sample(METADATA["politicians"], k=8)
            companies = random.sample(METADATA["companies"], k=3)
            people = random.sample(METADATA["people"], k=3)
            industries = random.sample(METADATA["industries"], k=11)
            legislations = random.sample(METADATA["legislations"], k=3)
            news_item = NewsItem(
                id=article.id,
                title=article.title,
                content=article.content,
                url=article.url,
                author=(
                    ", ".join(article.authors)
                    if article.authors
                    else "Unknown"
                ),
                published_at=(
                    article.published_at.strftime("%d %B %Y – %I:%M")
                    if article.published_at
                    else None
                ),
                language=article.language if article.language else None,
                category=(
                    ", ".join(article.categories)
                    if article.categories
                    else None
                ),
                summary=article.summary or "No summary available.",
                subscription_id=article.subscription.id,
                newspaper=article.subscription or "Unknown",
                keywords=[keyword.name for keyword in article.keywords],
                image_url=None,
                people=people,
                companies=companies,
                politicians=politicians,
                industries=industries,
                legislations=legislations,
            )
            news_items.append(news_item)
        search_profile = (
            await SearchProfileRepository.get_search_profile_by_id(
                search_profile_id
            )
        )
        return PDFService.draw_pdf(search_profile, news_items)

    @staticmethod
    def draw_pdf(
        search_profile: SearchProfile, news_items: List[NewsItem]
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
            search_profile, news_items, dimensions
        )
        summaries_elements = PDFService.__create_summaries_elements(
            news_items, dimensions
        )
        full_articles_elements = PDFService.__create_full_articles_elements(
            news_items, dimensions
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

        doc.addPageTemplates(
            [
                PageTemplate(id="Cover", frames=[frame]),
                PageTemplate(
                    id="SummariesThreeCol",
                    frames=frames,
                    onPage=PDFService.draw_header_footer,
                ),
                PageTemplate(
                    id="FullArticles",
                    frames=[full_article_frame],
                    onPage=PDFService.draw_header_footer,
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
                "<b> \
                   <font size=36>Daily News Report</font>\
                </b>",
                PDFService.styles["title_style"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))
        # Subtitle with current date and time
        now_str = datetime.today().strftime("%d %B %Y – %H:%M")
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
                label = "Estimated Reading Time: "
                canvas.drawString(0, 0, label)
                label_width = canvas.stringWidth(label, "DVS", 12)
                canvas.setFont("DVS-Bold", 12)
                canvas.drawString(label_width, 0, str(self.estimated_minutes))
                label_width += canvas.stringWidth(
                    str(self.estimated_minutes), "DVS-Bold", 12
                )
                canvas.drawString(label_width, 0, " min")

        story.append(EstimatedReadingTimeFlowable(total_minutes))
        story.append(Spacer(1, 0.3 * inch))

        # Add spacing before TOC
        story.append(Spacer(1, 12))

        # TOC Title (bold, styled)
        story.append(
            Paragraph(
                "Table of Contents",
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

            button_para = Paragraph(
                f"""
                <font backColor="{pdf_colors["lightgrey"]}" size="9">
                    <a href="#toc_summary_{i}">&nbsp;Summary&nbsp;</a>
                </font>
                &nbsp;&nbsp;
                <font backColor="{pdf_colors["lightgrey"]}" size="9">
                    <a href="#toc_article_{i}">&nbsp;Full Article&nbsp;</a>
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
    def draw_header_footer(canvas, doc):
        canvas.saveState()
        width, height = A4

        style = ParagraphStyle(
            name="HeaderTitle",
            fontName="DVS-BoldOblique",
            fontSize=10,
            textColor=pdf_colors["main"],
            leading=12,
        )

        now_str = datetime.today().strftime("%d %B %Y – %I:%M")

        data = [
            [
                Paragraph("<b>Daily News Report</b>", style),
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
        page_str = f"Page {doc.page}"
        canvas.drawRightString(width - inch, 0.4 * inch, page_str)

        canvas.restoreState()

    @staticmethod
    def __create_summaries_elements(
        news_items: List[NewsItem], dimensions: tuple[float, float]
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
            pub_date_str = ""
            if news.published_at:
                try:
                    dt = datetime.strptime(
                        # TODO inconsistent with previous time format
                        news.published_at.replace("Z", ""),
                        "%Y-%m-%dT%H:%M:%S",
                    )
                    pub_date_str = dt.strftime("%d %B %Y at %H:%M")
                except Exception:
                    pub_date_str = news.published_at
            story.append(
                Paragraph(pub_date_str, PDFService.styles["date_style"])
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
                    f'<a href="#{dest_name}">Read full article</a>',
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
        news_items: List[NewsItem], dimensions: tuple[float, float]
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
            Published at: {news.published_at} |
             Newspaper: {news.newspaper.name}
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
                Paragraph("Summary", PDFService.styles["subtitle_style"])
            )
            story.append(
                Paragraph(news.summary, PDFService.styles["content_style"])
            )
            story.append(Spacer(1, 0.15 * inch))

            story.append(
                Paragraph(
                    "Article Content", PDFService.styles["subtitle_style"]
                )
            )

            # Calculate reading time
            reading_time = calculate_reading_time(news.content)
            reading_time_text = f"Estimated Reading Time: {reading_time} min"
            reading_time_para = Paragraph(
                reading_time_text, PDFService.styles["link_style"]
            )
            read_summary_para = Paragraph(
                f"""
                <para alignment=\"right\">
                    <a href=\"#toc_summary_{i}\">\n
                    <u><font>Back to Summary List</font></u>\n
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
            # TODO: Content Extracted Data from DB and added to NewsItem
            # Prepare grouped Mentioned metadata
            people_str = ", ".join(f"{p}" for p in news.politicians)
            pol_str = ", ".join(f"{p}" for p in news.people)
            companies_str = ", ".join(f"{i}" for i in news.companies)
            industries_str = ", ".join(f"{i}" for i in news.industries)
            legislations_str = ", ".join(f"{i}" for i in news.legislations)

            # Prepare metadata as label-value pairs for two columns
            metadata_rows = [
                [
                    Paragraph("Words:", PDFService.styles["metadata_style"]),
                    Paragraph(
                        str(word_count), PDFService.styles["metadata_style"]
                    ),
                ],
                [
                    Paragraph(
                        "Reading Time:", PDFService.styles["metadata_style"]
                    ),
                    Paragraph(
                        f"{reading_time} min",
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph("Author:", PDFService.styles["metadata_style"]),
                    Paragraph(
                        news.author, PDFService.styles["metadata_style"]
                    ),
                ],
                [
                    Paragraph(
                        "Newspaper:", PDFService.styles["metadata_style"]
                    ),
                    Paragraph(
                        news.newspaper.name,
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        "<b>Published at:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        news.published_at, PDFService.styles["metadata_style"]
                    ),
                ],
                [
                    Paragraph(
                        "<b>Language:</b>", PDFService.styles["metadata_style"]
                    ),
                    Paragraph(
                        news.language or "Unknown",
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        "<b>Category:</b>", PDFService.styles["metadata_style"]
                    ),
                    Paragraph(
                        news.category or "Unknown",
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        "<b>Keywords:</b>", PDFService.styles["metadata_style"]
                    ),
                    Paragraph(
                        ", ".join(news.keywords) if news.keywords else "None",
                        PDFService.styles["metadata_style"],
                    ),
                ],
                [
                    Paragraph(
                        "<b>Mentioned in this article</b>",
                        PDFService.styles["metadata_subtitle_style"],
                    ),
                    "",
                ],
                [
                    Paragraph(
                        "<b>People:</b>", PDFService.styles["metadata_style"]
                    ),
                    Paragraph(people_str, PDFService.styles["metadata_style"]),
                ],
                [
                    Paragraph(
                        "<b>Politicians:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(pol_str, PDFService.styles["metadata_style"]),
                ],
                [
                    Paragraph(
                        "<b>Companies:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        companies_str, PDFService.styles["metadata_style"]
                    ),
                ],
                [
                    Paragraph(
                        "<b>Industries:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        industries_str, PDFService.styles["metadata_style"]
                    ),
                ],
                [
                    Paragraph(
                        "<b>Legislations:</b>",
                        PDFService.styles["metadata_style"],
                    ),
                    Paragraph(
                        legislations_str, PDFService.styles["metadata_style"]
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
                            f'<a href="{news.url}"><b>Read Article at \
                            Newspaper</b></a>',
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
