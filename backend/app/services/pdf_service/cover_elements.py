from typing import List
from reportlab.platypus import Flowable
from app.models.search_profile import SearchProfile
from .styles import get_pdf_styles
from .colors import pdf_colors
from .utils import calculate_reading_time
from reportlab.platypus import Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.platypus.flowables import AnchorFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from datetime import datetime

def draw_cover_elements(search_profile: SearchProfile, news_items: List, dimensions: tuple[float, float], styles) -> List[Flowable]:
    width, height = dimensions
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
    story.append(
        Paragraph(
            "<b> \\n               <font size=36>Daily News Report</font>\\
            </b>",
            styles["title_style"],
        )
    )
    story.append(Spacer(1, 0.3 * 72))
    now_str = datetime.today().strftime("%d %B %Y – %H:%M")
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
            canvas.setFont("DVS", 12)
            canvas.setFillColor(pdf_colors["darkgreen"])
            label = "Estimated Reading Time: "
            canvas.drawString(0, 0, label)
            label_width = canvas.stringWidth(label, "DVS", 12)
            canvas.setFont("DVS-Bold", 12)
            canvas.drawString(label_width, 0, str(self.estimated_minutes))
            label_width += canvas.stringWidth(str(self.estimated_minutes), "DVS-Bold", 12)
            canvas.drawString(label_width, 0, " min")
    story.append(EstimatedReadingTimeFlowable(total_minutes))
    story.append(Spacer(1, 0.3 * 72))
    story.append(Spacer(1, 12))
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
            styles["button_style"],
        )
        row = [[meta_para, button_para]]
        table = Table(row, colWidths=[4 * 72, 2 * 72])
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
