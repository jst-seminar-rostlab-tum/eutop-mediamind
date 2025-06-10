from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Frame, PageTemplate, Spacer, BaseDocTemplate, HRFlowable, PageBreak, NextPageTemplate, Table, TableStyle, Image, Flowable
from reportlab.platypus.flowables import AnchorFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.repositories.article_repository import ArticleRepository
from svglib.svglib import svg2rlg
from reportlab.graphics.shapes import Drawing
from PIL import Image as PILImage
import pillow_avif  # this automatically registers AVIF Images support with Pillow For downloading newspaper images
import requests # For feature downloading newspaper images
from io import BytesIO
import textwrap
from dataclasses import dataclass
from app.core.logger import get_logger

# TODO: Move colors to a separate module, Move only the needed styles to a Stylesheet, sample works with matching


#EUTOP colors #FFED00 #164194
mainColor=colors.HexColor("#003366")
blueColor=colors.HexColor("#164194")
electricBlue=colors.HexColor("#393be7")
yellowColor=colors.HexColor("#FFED00")
darkGrey=colors.HexColor("#525252")


@dataclass
class NewsItem:
    id: str
    title: str
    content: str
    url: str
    published_at: str
    summary: str
    subscription_id: str
    author: str | None = None
    language: str | None = None
    category: str | None = None
    newspaper: str | None = None
    keywords: list[str] | None = None
    image_url: str | None = None
    # Add optional fields for extracted data
    people: list | None = None
    companies: list | None = None
    politicians: list | None = None
    industries: list | None = None
    legislations: list | None = None
    

class PDFService:
    # Custom Fonts
    pdfmetrics.registerFont(TTFont("DVS", "assets/fonts/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DVS-Bold", "assets/fonts/DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("DVS-Oblique", "assets/fonts/DejaVuSans-Oblique.ttf"))
    pdfmetrics.registerFont(TTFont("DVS-BoldOblique", "assets/fonts/DejaVuSans-BoldOblique.ttf"))

    # Define commonly used styles as class variables
    link_style = ParagraphStyle('Link', fontName="DVS-BoldOblique", fontSize=8,
        textColor=electricBlue,
        spaceAfter=6,
        bulletIndent=0,
        leftIndent=6,
        leading=12,
        alignment=TA_JUSTIFY
    )
    newspaper_style = ParagraphStyle('Newspaper', fontName="DVS-Bold", fontSize=9, leading=11, textColor=blueColor)
    keywords_style = ParagraphStyle('Keywords', fontName="DVS-Oblique", fontSize=8, leading=10, textColor=blueColor)
    date_style = ParagraphStyle('Date', fontName="DVS-Oblique", fontSize=8, leading=10, textColor=colors.gray)
    summary_style = ParagraphStyle('Summary', fontName="DVS", fontSize=9, leading=12, alignment=TA_JUSTIFY)
    title_style = ParagraphStyle('Title', fontName="DVS-Bold", fontSize=16, leading=18, spaceAfter=12)
    metadata_style = ParagraphStyle('Metadata', fontName="DVS-Oblique", fontSize=9, leading=12, textColor=colors.gray)
    content_style = ParagraphStyle('Content', fontName="DVS", fontSize=11, leading=14, alignment=TA_JUSTIFY)

    @staticmethod
    async def create_sample_pdf() -> bytes:
        articles = await ArticleRepository.get_sameple_articles(15)
        news_items = []
        for article in articles:
            # Convert Article to NewsItem
            news_item = NewsItem(
                id=article.id,
                title=article.title,
                content=article.content,
                url=article.url,
                author=article.author.name if article.author else None,
                published_at=article.published_at.strftime("%d %B %Y – %I:%M%p") if article.published_at else None,
                language=article.language if article.language else None,
                category=article.category.name if article.category else None,
                summary=article.summary or "",
                subscription_id =article.subscription.id,
                newspaper=article.subscription.name,
                keywords=[keyword.name for keyword in article.keywords],
                image_url=None,  # Placeholder, as we don't have images in sample articles
                people=None,  # Placeholder, as we don't have people in sample articles
                companies=None,  # Placeholder, as we don't have companies in sample articles
                politicians=None,  # Placeholder, as we don't have politicians in sample articles
                industries=None,  # Placeholder, as we don't have industries in sample articles
                legislations=None  # Placeholder, as we don't have legislations in sample articles
            )
            # Replace the article with the news item
            news_items.append(news_item)
        return PDFService.create_pdf(news_items)

    @staticmethod
    def create_pdf(news_items: List[NewsItem]) -> bytes:
        dimensions = A4
        logger = get_logger(__name__)
        logger.info("Articles chosen before PDF Generation:")
        # Logging which articles, if they have summaries and keywords
        for news in news_items:
            logger.info(f"Processing News item: {news.id}, Summary: {True if news.summary else False}, Keywords: {True if news.keywords else 'False'}")

        # Prepare all flowable elements for the PDF
        cover_elements = PDFService.__draw_cover_elements(news_items, dimensions)
        summaries_elements = PDFService.__create_summaries_elements(news_items, dimensions)
        full_articles_elements = PDFService.__create_full_articles_elements(news_items, dimensions)
        # Combine all elements
        all_elements = []
        all_elements.append(NextPageTemplate('Cover'))
        all_elements.extend(cover_elements)
        # Add NextPageTemplate to switch to three-column layout for summaries
        all_elements.append(NextPageTemplate('SummariesThreeCol'))
        all_elements.append(PageBreak())
        all_elements.extend(summaries_elements)
        # Switch back to full-width single-column layout for full articles
        all_elements.append(NextPageTemplate('FullArticles'))
        all_elements.append(PageBreak())
        all_elements.extend(full_articles_elements)

        buffer = BytesIO()
        width, height = dimensions
        margin = inch

        # Use a single frame for simplicity, as elements can use PageBreaks
        frame = Frame(margin, margin, width - 2*margin, height - 2*margin, id='main')

        # Define a full-width frame for full articles
        full_article_frame = Frame(margin, margin, width - 2*margin, height - 2*margin, id='full_article')
        
        # Define three vertical frames evenly spaced across the page width for summaries
        frame_width = (width - 2 * margin) / 3
        frames = [
            Frame(margin + i * frame_width, margin, frame_width, height - 2 * margin, id=f'col{i}')
            for i in range(3)
        ]
        
        doc = BaseDocTemplate(buffer, pagesize=A4, rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=margin)

        doc.addPageTemplates([
            PageTemplate(id='Cover', frames=[frame]),
            PageTemplate(id="SummariesThreeCol", frames=frames, onPage=PDFService.draw_header_footer),
            PageTemplate(id='FullArticles', frames=[full_article_frame], onPage=PDFService.draw_header_footer)
        ])
        doc.build(all_elements)
        buffer.seek(0)
        return buffer.getvalue()


    # This function wraps text to a specified width, ensuring that it fits within the PDF layout.
    # @staticmethod
    # def __wrap_text(text, width):
    #     wrapper = textwrap.TextWrapper(width=width)
    #     return "\n".join(wrapper.wrap(text))

    # This function calculates the estimated reading time based on the word count and a specified reading speed. 
    @staticmethod 
    def __calculate_reading_time(text, words_per_minute=180):
        word_count = len(text.split())
        return max(1, int(round(word_count / words_per_minute)))

    @staticmethod
    def __draw_cover_elements(news_items: List[NewsItem], dimensions: tuple[float, float]) -> List['Flowable']:
        width, height = dimensions
        styles = getSampleStyleSheet()

        style = ParagraphStyle(
            name="HeaderTitle",
            fontName="DVS",
            fontSize=10,
            alignment=TA_JUSTIFY)

        # TOC entry style
        toc_entry_style = ParagraphStyle(
            name="TOCEntry",
            fontName="DVS-Bold",
            fontSize=10,
            textColor=blueColor,
            spaceAfter=0,
            bulletIndent=0,
            leftIndent=0,
            leading=14,
            alignment=TA_JUSTIFY
        )

        metadata_style = ParagraphStyle(
            name="HeaderTitle",
            fontName="DVS",
            fontSize=10,
            textColor=darkGrey,
            spaceAfter=6,
            bulletIndent=0,
            leftIndent=6,
            leading=6,
            alignment=TA_JUSTIFY
        )

        story = []
        # Logo
        try:
            drawing = svg2rlg("assets/eutop_logo.svg")
            scale = 0.7
            drawing.scale(scale, scale)
            drawing.width *= scale
            drawing.height *= scale
            from reportlab.graphics.shapes import Drawing
            drawing_wrapper = Drawing(width, drawing.height)
            drawing_wrapper.add(drawing, name="logo")
            drawing_wrapper.translate((width - drawing.width) / 4, 0)
            story.append(drawing_wrapper)
        except Exception as e:
            print(f"Error loading SVG logo: {e}")
        story.append(Spacer(1, 0.5 * inch))
        # Title
        # TODO: Read from DB the Search Profile Name to indivualize Report
        story.append(Paragraph(f"<b><font size=36 color='{electricBlue}'>BMW EX</font></b>", styles['Title']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("<b><font size=36 color='#003366'>Daily News Report</font></b>", styles['Title']))
        story.append(Spacer(1, 0.4 * inch))
        # Subtitle with current date and time
        now_str = datetime.today().strftime("%d %B %Y – %I:%M%p")
        story.append(Paragraph(f"<b><font size=16 color='#003366'>{now_str}</font></b>", styles['Title']))
        story.append(Spacer(1, 0.3 * inch))
        # Total reading time
        total_text = " ".join(news.content for news in news_items)
        total_minutes = PDFService.__calculate_reading_time(total_text, words_per_minute=180)
        story.append(Paragraph(f"<font size=12 color='darkgreen'>Estimated Reading Time: {total_minutes} min</font>", style))
        story.append(Spacer(1, 0.3 * inch))
        
        # --- Improved Table of Contents Styling ---
        # Add spacing before TOC
        story.append(Spacer(1, 12))
        
        # TOC Title (bold, styled)
        story.append(Paragraph("Table of Contents", ParagraphStyle(name="TOCHeader", fontName="DVS-Bold", fontSize=16, spaceAfter=12, textColor=blueColor)))
        # Horizontal rule before TOC
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceBefore=6, spaceAfter=6))


        # TOC entries
        for i, news in enumerate(news_items):
            # Add anchor for TOC entry (optional, if needed)
            story.append(AnchorFlowable(f"toc_entry_{i}"))
            story.append(
                Paragraph(
                    f'<a href="#toc_summary_{i}">{i+1}. {news.title}</a><br/>',
                    toc_entry_style
                )
            )
            meta_para = Paragraph(f'<font size="9">{news.newspaper}, {news.published_at}</font>', metadata_style)
            button_para = Paragraph(f'''
                <font backColor="{yellowColor}" size="9">
                    <a href="#toc_summary_{i}">  Summary  </a>
                </font>
                &nbsp;&nbsp;
                <font backColor="{yellowColor}" size="9">
                    <a href="#toc_article_{i}">  Full Article  </a>
                </font>
            ''', PDFService.link_style)

            row = [[meta_para, button_para]]
            table = Table(row, colWidths=[3.5 * inch, 2.5 * inch])  # Adjust as needed
            table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]))

            story.append(table)
            
            story.append(Spacer(1, 12))

        # Horizontal rule after TOC
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceBefore=6, spaceAfter=6))
        # Add spacing after TOC
        story.append(Spacer(1, 12))
        return story
    
    @staticmethod
    def draw_header_footer(canvas, doc):
        canvas.saveState()
        width, height = A4
        # Draw the background
        #canvas.setFillColor(colors.HexColor("#e6f0fa"))
        #canvas.rect(0, 0, width, height, fill=1, stroke=0)

        # Use a styled ParagraphStyle for header, matching title font and color
        style = ParagraphStyle(
            name="HeaderTitle",
            fontName="DVS-BoldOblique",
            fontSize=10,
            textColor=colors.HexColor("#003366"),
            leading=12
        )

        now_str = datetime.today().strftime("%d %B %Y – %I:%M%p")

        # Load and scale SVG logo
        try:
            drawing = svg2rlg("assets/eutop_logo.svg")
            target_height = 0.17 * inch
            scale = target_height / drawing.height
            drawing.width *= scale
            drawing.height *= scale
            drawing.scale(scale, scale)

            # Wrap in a Drawing for compatibility in table
            wrapped_drawing = Drawing(drawing.width, drawing.height)
            wrapped_drawing.add(drawing)
        except Exception as e:
            print(f"Could not load logo: {e}")
            wrapped_drawing = ""

        # Construct table with Header,Time,SVG
        data = [
            [
                Paragraph("<b>Daily News Report</b>", style),
                Paragraph(f"<b>{now_str}</b>", style),
                wrapped_drawing
            ]
        ]
        table = Table(data, colWidths=[2.5 * inch, 2.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
        ]))
        table.wrapOn(canvas, width, height)
        table.drawOn(canvas, inch, height - inch + 20)

        # --- Draw page number in footer ---
        canvas.setFont("DVS", 10)
        canvas.setFillColor(colors.HexColor("#003366"))
        page_str = f"Page {doc.page}"
        canvas.drawRightString(width - inch, 0.4 * inch, page_str)

        canvas.restoreState()


    @staticmethod
    def __create_summaries_elements(news_items: List[NewsItem], dimensions: tuple[float, float]) -> List['Flowable']:
        width, height = dimensions
        story = []
        for i, news in enumerate(news_items):
            story.append(AnchorFlowable(f"toc_summary_{i}"))
            story.append(Paragraph(str(i+1) + '. '+ news.title or "", PDFService.newspaper_style))
            story.append(Spacer(1, 0.05 * inch))
            story.append(Paragraph(f'<link href="{news.url}">{news.newspaper}</link>' or "", PDFService.keywords_style))
            pub_date_str = ""
            if news.published_at:
                try:
                    dt = datetime.strptime(news.published_at.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
                    pub_date_str = dt.strftime("%d %B %Y at %H:%M")
                except Exception:
                    pub_date_str = news.published_at
            story.append(Paragraph(pub_date_str, PDFService.date_style))
            story.append(Spacer(1, 0.05 * inch))
            summary_text = news.content[:300].replace('\n', '<br/>')
            story.append(Paragraph(summary_text, PDFService.summary_style))
            story.append(Spacer(1, 0.05 * inch))
            dest_name = f"full_{news.id}"
            story.append(Paragraph(f'<a href="#{dest_name}">Read full article</a>', PDFService.link_style))
            story.append(Spacer(1, 0.15 * inch))
            if i != len(news_items) - 1:
                story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#003366")))
                story.append(Spacer(1, 0.2 * inch))
        return story

    @staticmethod
    def __create_full_articles_elements(news_items: List[NewsItem], dimensions: tuple[float, float]) -> List['Flowable']:
        story = []
        for i, news in enumerate(news_items):
            dest_name = f"full_{news.id}"
            story.append(AnchorFlowable(dest_name))
            story.append(AnchorFlowable(f"toc_article_{i}"))
            story.append(Paragraph(str(i+1) + '. ' + news.title, PDFService.title_style))
            word_count = len(news.content.split()) if news.content else 0
            newspaper = news.newspaper or "Unknown"
            author = news.author or "Unknown"
            pub_date_str = ""
            if news.published_at:
                try:
                    dt = datetime.strptime(news.published_at.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
                    pub_date_str = dt.strftime("%d %B %Y")
                except Exception:
                    pub_date_str = news.published_at
            metadata_text = f"Words: {word_count} | Newspaper: {newspaper} | Date: {pub_date_str} | Author: {author}"
            story.append(Paragraph(metadata_text, PDFService.metadata_style))
            story.append(Paragraph(f'''
                                    <para alignment="right">
                                   <a href="#toc_summary_{i}"><u><font>Read summary</font></u></a>
                                    </para>
                                   '''
                                   , PDFService.link_style))
            story.append(Spacer(1, 0.15 * inch))

            #Content
            content_text = news.content.replace('\n', '<br/>')
            story.append(Paragraph(content_text, PDFService.content_style))
            story.append(Spacer(1, 0.3 * inch))

            #TODO: Content Extracted Data from DB and added to NewsItem
            people_str = "None"
            if hasattr(news, "politicians") and isinstance(news.politicians, list) and news.politicians:
                people_str = ", ".join(f"{p.name}" for p in news.politicians if hasattr(p, "name"))
            story.append(Paragraph(f'<b>Mentioned People: </b> {people_str}', PDFService.metadata_style))

            pol_str = "None"
            if hasattr(news, "people") and isinstance(news.people, list) and news.people:
                pol_str = ", ".join(f"{p.name} ({getattr(p, 'party', 'N/A')})" for p in news.people if hasattr(p, "name"))
            story.append(Paragraph(f'<b>Mentioned Politicians: </b> {pol_str}', PDFService.metadata_style))

            companies_str = "None"
            if hasattr(news, "companies") and isinstance(news.companies, list) and news.companies:
                companies_str = ", ".join(f"{comp.name}" for comp in news.companies if hasattr(comp, "name"))
            story.append(Paragraph(f'<b>Mentioned Companies: </b> {companies_str}', PDFService.metadata_style))

            industries_str = "None"
            if hasattr(news, "industries") and isinstance(news.industries, list) and news.industries:
                industries_str = ", ".join(f"{ind.name}" for ind in news.industries if hasattr(ind, "name"))
            story.append(Paragraph(f'<b>Mentioned Industries: </b> {industries_str}', PDFService.metadata_style))

            legislations_str = "None"
            if hasattr(news, "legislations") and isinstance(news.legislations, list) and news.legislations:
                legislations_str = ", ".join(f"{getattr(leg, 'number', 'N/A')} ({getattr(leg, 'name', 'N/A')})" for leg in news.legislations)
            story.append(Paragraph(f'<b>Mentioned Legislations: </b> {legislations_str}', PDFService.metadata_style))


            # URL Link Button
            link_img = Image("assets/link_icon.png", width=16, height=16)
            button = Table(
                [[
                    link_img,
                    Paragraph(f'<a href="{news.url}"><b>Read Article at Newspaper</b></a>', PDFService.link_style)
                ]],
                colWidths=[0.2 * inch, 2.1 * inch],
                hAlign='RIGHT'
            )
            button.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 0), (-1, -1), blueColor),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("INNERGRID", (0, 0), (-1, -1), 0, colors.white),
                ("BOX", (0, 0), (-1, -1), 1, blueColor),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            story.append(button)        

            if i != len(news_items) - 1:
                story.append(PageBreak())
        return story