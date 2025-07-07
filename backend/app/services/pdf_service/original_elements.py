from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable
from reportlab.platypus.flowables import AnchorFlowable
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from .colors import pdf_colors
from .markdown_utils import markdown_blocks_to_paragraphs

def create_original_articles_elements(news_items, styles, translator):
    """
    Returns a list of Flowables for the appendix with all original-language articles.
    Each article gets an anchor for linking from the full article, and a backlink to the full article.
    """
    elements = []
    appendix_title = translator("Appendix: Original Articles")
    elements.append(PageBreak())
    elements.append(AnchorFlowable("appendix_start"))
    elements.append(Paragraph(f"<b>{appendix_title}</b>", styles["title_style"]))
    elements.append(Spacer(1, 0.3 * inch))

    for i, news in enumerate(news_items):
        # Anchor for this original article
        elements.append(AnchorFlowable(f"original_article_{i}"))
        # Title in original language (not translated)
        elements.append(Paragraph(f"<b>{news.title}</b>", styles["title_style"]))
        # Link back to full article
        elements.append(Paragraph(
            f'<a href="#toc_article_{i}">{translator("Back to translated article")}</a>',
            styles["button_style"]
        ))
        elements.append(Spacer(1, 0.1 * inch))
        # Newspaper and date
        elements.append(Paragraph(
            f'<font size="10">{news.newspaper.name if hasattr(news.newspaper, "name") else news.newspaper} | {news.published_at}</font>',
            styles["metadata_style"]
        ))
        elements.append(Spacer(1, 0.1 * inch))
        for para in markdown_blocks_to_paragraphs(news.content, styles):
            elements.append(para)
        elements.append(Spacer(1, 0.2 * inch))
        # Link back to translated article
        elements.append(Paragraph(
            f'<a href="#toc_article_{i}">{translator("Back to translated article")}</a>',
            styles["button_style"]
        ))
        # Pagebreak
        if i < len(news_items) - 1:
            elements.append(PageBreak())
        
    return elements