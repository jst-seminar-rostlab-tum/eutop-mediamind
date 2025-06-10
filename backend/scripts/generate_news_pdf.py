from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics import renderPDF
from reportlab.platypus import Paragraph, Frame, Spacer, Image
from reportlab.platypus.flowables import AnchorFlowable
from reportlab.lib.styles import ParagraphStyle
from svglib.svglib import svg2rlg
from PIL import Image as PILImage
import pillow_avif  # this automatically registers AVIF Images support with Pillow
import json
import requests
from io import BytesIO
import textwrap
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, NextPageTemplate, PageBreak
from datetime import datetime
from reportlab.platypus import HRFlowable
import os
from PyPDF2 import PdfMerger, PdfReader

# This function wraps text to a specified width, ensuring that it fits within the PDF layout.
def wrap_text(text, width):
    wrapper = textwrap.TextWrapper(width=width)
    return "\n".join(wrapper.wrap(text))

# This function calculates the estimated reading time based on the word count and a specified reading speed.
def calculate_reading_time(text, words_per_minute=180):
    word_count = len(text.split())
    return max(1, int(round(word_count / words_per_minute)))

def draw_cover_page(file_path, news_items, width, height):
    from reportlab.platypus import Paragraph, Spacer, Frame, PageTemplate
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import Flowable

    doc = BaseDocTemplate(file_path, pagesize=A4)
    frame = Frame(inch, inch, width - 2*inch, height - 2*inch)

    # Draw background using onPage method for consistent background rendering
    def draw_cover_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#e6f0fa"))
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id='Cover', frames=frame, onPage=draw_cover_background)])
    styles = getSampleStyleSheet()

    story = []

    # Logo
    try:
        drawing = svg2rlg("scripts/eutop_logo.svg")
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
    story.append(Paragraph("<b><font size=36 color='#003366'>Daily News Report</font></b>", styles['Title']))
    story.append(Spacer(1, 0.3 * inch))
    # Subtitle with current date and time
    now_str = datetime.today().strftime("Time %H:%M – %d %B %Y")
    story.append(Paragraph(f"<b><font size=16 color='#003366'>{now_str}</font></b>", styles['Title']))
    story.append(Spacer(1, 0.4 * inch))

    # Total reading time
    total_text = " ".join(news['content'] for news in news_items)
    total_minutes = calculate_reading_time(total_text, words_per_minute=100)
    story.append(Paragraph(f"<font size=12 color='darkgreen'>Total Estimated Reading Time: {total_minutes} min</font>", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))

    # TOC # Not working
    story.append(Paragraph("<b><font size=16 color='#003366'>Table of Contents</font></b>", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    for news in news_items:
        toc_line = f"{news['title']} ({news['newspaper']}, {news.get('date_time', '')})"
        story.append(Paragraph(toc_line, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

    doc.build(story)

def draw_header_footer(canvas, doc):
    width, height = A4
    #Draw the background
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#e6f0fa"))
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.restoreState()

    now = datetime.today()
    time_part = now.strftime("%H:%M")
    date_part = now.strftime("%d %B %Y")

    # Draw start of header
    y_position = height - inch + 5
    x_start = inch
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(colors.HexColor("#003366"))
    canvas.drawString(x_start, y_position, "Continued News Report")

    #Time
    x_after = x_start + canvas.stringWidth("Continued News Report   –   ", "Helvetica-Bold", 15)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawString(x_after, y_position, time_part + " ")

    #Date
    x_after += canvas.stringWidth(time_part + " ", "Helvetica-Oblique", 10)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(x_after, y_position, date_part)

    # Draw end of header
    try:
        drawing = svg2rlg("scripts/eutop_logo.svg")
        target_height = 0.17 * inch
        scale = target_height / drawing.height
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
        renderPDF.draw(drawing, canvas, width - inch - drawing.width, height - inch + 15 - drawing.height + 2)
    except Exception as e:
        print(f"Could not load logo: {e}")

    # Draw footer with Page number
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.HexColor("#003366"))
    page_str = f"Page {doc.page}"
    canvas.drawRightString(width - inch, 0.4 * inch, page_str)

def create_news_pdf(file_name, news_items):
    width, height = A4
    column_width = (width - 2 * inch) / 3
    gutter = 0.15 * inch
    # Define top and bottom margins to allow space for header and footer
    top_margin = 1.25 * inch  # space for header
    bottom_margin = 1.0 * inch  # space for footer
    content_height = height - top_margin - bottom_margin
    col_x = [inch + (column_width + gutter) * i for i in range(3)]
    frames = [Frame(x, bottom_margin, column_width, content_height, id=f'col{i}', showBoundary=0) for i, x in enumerate(col_x)]

    doc = BaseDocTemplate(file_name, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()

    keywords_style = styles["Normal"]
    keywords_style.fontName = "Helvetica-Oblique"
    keywords_style.fontSize = 8
    keywords_style.leading = 10
    keywords_style.textColor = colors.HexColor("#003366")

    summary_style = styles["Normal"]
    summary_style.fontName = "Helvetica-Oblique"
    summary_style.fontSize = 9
    summary_style.leading = 12
    summary_style.textColor = colors.darkgray

    content_style = styles["Normal"]
    content_style.fontName = "Helvetica"
    content_style.fontSize = 10
    content_style.leading = 12

    reading_time_style = styles["Normal"]
    reading_time_style.fontName = "Helvetica-Oblique"
    reading_time_style.fontSize = 9
    reading_time_style.leading = 12
    reading_time_style.textColor = colors.darkgreen

    para_style = ParagraphStyle('ColumnContent', fontName="Helvetica", fontSize=10, leading=12)

    story = []

    for news in news_items:
        anchor_name = f"dest_{news['title'].replace(' ', '_')}"
        story.append(AnchorFlowable(anchor_name))
        story.append(Paragraph(f"<b>{news['title']}</b>", styles['Heading3']))
        if 'date_time' in news and news['date_time']:
            try:
                dt = datetime.strptime(news['date_time'].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
                time_str = f"<b>Time:</b> <b>{dt.strftime('%H:%M')}</b> <i>{dt.strftime('%d/%m/%y')}</i>"
            except Exception:
                time_str = news['date_time']
            story.append(Paragraph(time_str, reading_time_style))
            story.append(Spacer(1, 0.1 * inch))

        if 'image_url' in news and news['image_url']:
            try:
                response = requests.get(news['image_url'])
                img_data = BytesIO(response.content)
                pil_img = PILImage.open(img_data)
                aspect = pil_img.height / float(pil_img.width)
                img_data.seek(0)
                img = Image(img_data, width=column_width, height=(column_width * aspect))
                story.append(img)
                story.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                print(f"Error loading image: {e}")

        story.append(Paragraph(f"<b>Newspaper:</b> {news['newspaper']}", content_style))
        story.append(Spacer(1, 0.1 * inch))

        keywords_str = ", ".join(news['keywords'])
        story.append(Paragraph(f"<b>Keywords:</b> {keywords_str}", keywords_style))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph(f"<b>Summary:</b> {news['summary']}", summary_style))
        story.append(Spacer(1, 0.1 * inch))

        estimated_minutes = calculate_reading_time(news['content'], words_per_minute=180)
        story.append(Paragraph(f"<b>Estimated Reading Time:</b> {estimated_minutes} min", reading_time_style))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph(news['content'], para_style))
        story.append(Spacer(1, 0.2 * inch))

        if news != news_items[-1]:
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#003366")))
            story.append(Spacer(1, 0.2 * inch))

    doc.addPageTemplates([PageTemplate(id='ThreeCol', frames=frames, onPage=draw_header_footer)])
    doc.build(story)

    # Generate cover page to separate PDF
    cover_path = "cover_temp.pdf"
    draw_cover_page(cover_path, news_items, width, height)

    # Merge main report first, then cover at position 0
    merger = PdfMerger()
    merger.append(PdfReader(file_name))
    merger.merge(position=0, fileobj=PdfReader(cover_path))
    merger.write(file_name)
    merger.close()
    os.remove(cover_path)

    print(f"PDF generated: {file_name}")



if __name__ == "__main__":
    with open("scripts/dummy_news.json") as f:
        news_list = json.load(f)
    create_news_pdf("daily_news_report.pdf", news_list)