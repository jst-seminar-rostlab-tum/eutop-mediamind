from datetime import datetime
from typing import List

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import AnchorFlowable

from .colors import pdf_colors
from .utils import calculate_reading_time


def draw_cover_elements(
    news_items: List,
    dimensions: tuple[float, float],
    styles,
    translator,
):
    width, height = dimensions
    toc_entry_style = ParagraphStyle(
        name="TOCEntry",
        fontName="Bold",
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
        fontName="Regular",
        fontSize=10,
        textColor=pdf_colors["darkGrey"],
        spaceAfter=6,
        bulletIndent=0,
        leftIndent=6,
        leading=10,
        alignment=TA_JUSTIFY,
    )
    story = []
    story.append(
        Paragraph(
            f"<b> <font size=36>{translator('Current Press Report')}</font></b>",  # noqa 501
            styles["title_style"],
        )
    )
    story.append(Spacer(1, 0.3 * 72))
    now = datetime.today()
    month = now.strftime("%B")
    now_str = (
        f"{now.strftime('%d')} {translator(month)} {now.strftime('%Y')} – "
        f"{now.strftime('%H:%M')}"
    )
    story.append(
        Paragraph(
            f"<b><font size=16>{now_str}</font></b>",
            styles["title_style"],
        )
    )
    story.append(Spacer(1, 0.3 * 72))
    total_text = " ".join(news.content for news in news_items)
    total_minutes = calculate_reading_time(total_text, words_per_minute=180)

    class EstimatedReadingTimeFlowable(Flowable):
        def __init__(self, estimated_minutes):
            super().__init__()
            self.estimated_minutes = estimated_minutes

        def wrap(self, available_width, available_height):
            return available_width, 16

        def draw(self):
            canvas = self.canv
            canvas.setFont("Regular", 12)
            canvas.setFillColor(pdf_colors["darkgreen"])
            label = translator("Estimated Reading Time") + ": "
            canvas.drawString(0, 0, label)
            label_width = canvas.stringWidth(label, "Regular", 12)
            canvas.setFont("Bold", 12)
            canvas.drawString(label_width, 0, str(self.estimated_minutes))
            label_width += canvas.stringWidth(
                str(self.estimated_minutes), "Bold", 12
            )
            canvas.drawString(label_width, 0, f" {translator('min')}")

    story.append(EstimatedReadingTimeFlowable(total_minutes))
    story.append(Spacer(1, 0.3 * 72))
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            translator("Table of Contents"),
            ParagraphStyle(
                name="TOCHeader",
                fontName="Bold",
                fontSize=16,
                spaceAfter=12,
                textColor=pdf_colors["blue"],
            ),
        )
    )
    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=pdf_colors["gray"],
            spaceBefore=6,
            spaceAfter=6,
        )
    )
    for i, news in enumerate(news_items):
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
        from reportlab.lib.enums import TA_RIGHT

        button_style_right = styles["button_style"].clone("button_style_right")
        button_style_right.alignment = TA_RIGHT
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
            button_style_right,
        )
        row = [[meta_para, button_para]]
        table = Table(row, colWidths=[5 * cm, 8 * cm], hAlign="LEFT")
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
    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=pdf_colors["gray"],
            spaceBefore=6,
            spaceAfter=6,
        )
    )
    story.append(Spacer(1, 12))
    return story
