from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import pillow_avif  # this automatically registers AVIF Images support with Pillow
import json
import requests
from io import BytesIO
import textwrap

# This function wraps text to a specified width, ensuring that it fits within the PDF layout.
def wrap_text(text, width):
    wrapper = textwrap.TextWrapper(width=width)
    return "\n".join(wrapper.wrap(text))

# This function calculates the estimated reading time based on the word count and a specified reading speed.
def calculate_reading_time(text, words_per_minute=180):
    word_count = len(text.split())
    return max(1, int(round(word_count / words_per_minute)))

def draw_cover_page(c, news_items, width, height):
    y_position = height - 1.5 * inch
    # Draw EUTOP SVG Logo
    try:
        drawing = svg2rlg("scripts/eutop_logo.svg")
        renderPDF.draw(drawing, c, inch, y_position - 2 * inch)
    except Exception as e:
        print(f"Error loading SVG logo: {e}")

    # Title
    y_position -= 2.5 * inch
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0.0, 0.2, 0.6)
    c.drawCentredString(width / 2, y_position, "Daily News Report")
    y_position -= 0.5 * inch

    # Total reading time
    total_text = " ".join(news['content'] for news in news_items)
    total_minutes = calculate_reading_time(total_text, words_per_minute=100)
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.darkgreen)
    c.drawCentredString(width / 2, y_position, f"Total Estimated Reading Time: {total_minutes} min")

    # Table of Contents
    y_position -= inch
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.0, 0.2, 0.6)
    c.drawString(inch, y_position, "Table of Contents")
    c.setFillColor(colors.black)
    y_position -= 0.5 * inch
    c.setFont("Helvetica", 11)
    for news in news_items:
        toc_line = f"{news['title']} ({news['newspaper']}, {news.get('date_time', '')})"
        if y_position < inch:
            c.showPage()
            y_position = height - inch
            c.setFont("Helvetica", 11)
        c.drawString(inch, y_position, toc_line)
        y_position -= 0.3 * inch

def create_news_pdf(file_name, news_items):
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4
    draw_cover_page(c, news_items, width, height)
    c.showPage()

    # Start news articles on new page
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.0, 0.2, 0.6)
    c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")
    c.setFillColor(colors.black)
    y_position = height - inch

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

    for news in news_items:
        if y_position < 2 * inch:
            c.showPage()
            c.setFont("Helvetica", 9)
            c.setFillColorRGB(0.0, 0.2, 0.6)
            c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")
            c.setFillColor(colors.black)
            y_position = height - inch
            c.setFont("Helvetica-Bold", 16)
            c.setFillColorRGB(0.0, 0.2, 0.6)
            c.drawString(inch, y_position, "Continued News Report")
            c.setFillColor(colors.black)
            y_position -= 0.4 * inch

        c.setFillColorRGB(0.0, 0.2, 0.6)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_position, news['title'])

        # Draw Date/Time on the same line, right-aligned, formatted as "Time" (bold), hour+minute (bold), and date (italic)
        if 'date_time' in news and news['date_time']:
            from datetime import datetime
            try:
                dt = datetime.strptime(news['date_time'].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
            except Exception:
                dt = None
            if dt:
                time_label = "Time:"
                time_part = dt.strftime("%H:%M")
                date_part = dt.strftime("%d/%m/%y")

                c.setFont("Helvetica-Bold", 11)
                time_label_width = c.stringWidth(time_label, "Helvetica-Bold", 11)
                time_part_width = c.stringWidth(time_part, "Helvetica-Bold", 11)

                c.setFont("Helvetica-Oblique", 9)
                date_part_width = c.stringWidth(date_part, "Helvetica-Oblique", 9)

                total_width = time_label_width + 6 + time_part_width + 6 + date_part_width
                x_start = width - inch - total_width

                c.setFont("Helvetica-Bold", 11)
                c.drawString(x_start, y_position, time_label)
                c.drawString(x_start + time_label_width + 2, y_position, time_part)

                c.setFont("Helvetica-Oblique", 9)
                c.drawString(x_start + time_label_width + 6 + time_part_width + 6, y_position, date_part)
            else:
                # fallback: just print raw date_time
                c.setFont("Helvetica-BoldOblique", 10)
                time_text_width = c.stringWidth(news['date_time'], "Helvetica-BoldOblique", 10)
                c.drawString(width - inch - time_text_width, y_position, news['date_time'])

        c.setFillColor(colors.black)
        y_position -= 0.25 * inch

        # Draw date/time below newspaper name (already drawn above, so skip here)

        # Draw image if possible, scaled to 1/3 of original size
        if 'image_url' in news and news['image_url']:
            try:
                response = requests.get(news['image_url'])
                image = ImageReader(BytesIO(response.content))
                img_width, img_height = image.getSize()
                img_display_width = img_width / 3
                img_display_height = img_height / 3
                if y_position - img_display_height < inch:
                    c.showPage()
                    c.setFont("Helvetica", 9)
                    c.setFillColorRGB(0.0, 0.2, 0.6)
                    c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")
                    c.setFillColor(colors.black)
                    y_position = height - inch
                c.drawImage(image, inch, y_position - img_display_height, width=img_display_width, height=img_display_height)
                y_position -= img_display_height + 0.3 * inch
            except Exception as e:
                print(f"Error loading image: {e}")

        c.setFont("Helvetica-Oblique", 11)
        c.drawString(inch, y_position, f"Newspaper: {news['newspaper']}")
        y_position -= 0.25 * inch

        # Draw Keywords with smaller font and distinct style
        keywords_str = ", ".join(news['keywords'])
        text_obj = c.beginText(inch, y_position)
        text_obj.setFont(keywords_style.fontName, keywords_style.fontSize)
        text_obj.setFillColor(keywords_style.textColor)
        text_obj.textLine(f"Keywords: {keywords_str}")
        c.drawText(text_obj)
        y_position -= keywords_style.leading + 0.1 * inch

        # Draw Summary with word wrap
        summary_text = wrap_text(f"Summary: {news['summary']}", 90)
        text_obj = c.beginText(inch, y_position)
        text_obj.setFont(summary_style.fontName, summary_style.fontSize)
        text_obj.setFillColor(summary_style.textColor)
        for line in summary_text.split('\n'):
            text_obj.textLine(line)
            y_position -= summary_style.leading
        c.drawText(text_obj)
        y_position -= 0.1 * inch

        # Calculate and draw estimated reading time
        estimated_minutes = calculate_reading_time(news['content'], words_per_minute=180)
        reading_time_text = f"Estimated Reading Time: {estimated_minutes} min"
        text_obj = c.beginText(inch, y_position)
        text_obj.setFont(reading_time_style.fontName, reading_time_style.fontSize)
        text_obj.setFillColor(reading_time_style.textColor)
        text_obj.textLine(reading_time_text)
        c.drawText(text_obj)
        y_position -= reading_time_style.leading + 0.1 * inch

        # Draw Content with word wrap
        content_text = wrap_text(news['content'], 90)
        text_obj = c.beginText(inch, y_position)
        text_obj.setFont(content_style.fontName, content_style.fontSize)
        text_obj.setFillColor(colors.black)
        for line in content_text.split('\n'):
            text_obj.textLine(line)
            y_position -= content_style.leading
        c.drawText(text_obj)
        y_position -= 0.2 * inch

        y_position -= 0.2 * inch

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.0, 0.2, 0.6)
    c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")
    c.setFillColor(colors.black)

    c.save()
    print(f"PDF generated: {file_name}")



if __name__ == "__main__":
    with open("scripts/dummy_news.json") as f:
        news_list = json.load(f)
    create_news_pdf("daily_news_report.pdf", news_list)