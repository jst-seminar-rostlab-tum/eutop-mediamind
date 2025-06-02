from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pillow_avif  # this automatically registers AVIF support with Pillow
import json
import requests
from io import BytesIO
import textwrap


def create_news_pdf(file_name, news_items):
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4
    y_position = height - inch

    # Draw logo image next to title
    try:
        logo = ImageReader("eutop_logo.png")
        logo_width, logo_height = logo.getSize()
        logo_display_height = 0.5 * inch
        logo_display_width = logo_width * (logo_display_height / logo_height)
        c.drawImage(logo, inch, y_position - logo_display_height + 4, logo_display_width, logo_display_height)
    except:
        logo_display_width = 0

    c.setFont("Helvetica-Bold", 18)
    title_x = inch + logo_display_width + 0.2 * inch
    c.drawString(title_x, y_position, "Daily News Report")
    y_position -= 0.4 * inch

    # Calculate total estimated reading time for all articles
    total_words = sum(len(news['content'].split()) for news in news_items)
    total_minutes = max(1, int(round(total_words / 180)))
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(colors.darkgreen)
    c.drawString(title_x, y_position, f"Total Estimated Reading Time: {total_minutes} min")
    c.setFillColor(colors.black)
    y_position -= 0.3 * inch

    # Add Table of Contents on the same page
    c.setFont("Helvetica-Bold", 16)
    toc_y = y_position
    c.drawString(inch, toc_y, "Table of Contents")
    toc_y -= 0.5 * inch
    c.setFont("Helvetica", 11)
    for news in news_items:
        date_time_str = news.get('date_time', '')
        toc_line = f"{news['title']} ({news['newspaper']}, {date_time_str})"
        if toc_y < inch:
            c.showPage()
            c.setFont("Helvetica", 9)
            c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")
            toc_y = height - inch
            c.setFont("Helvetica", 11)
        c.drawString(inch, toc_y, toc_line)
        toc_y -= 0.3 * inch

    # Start news articles on new page
    c.showPage()
    c.setFont("Helvetica", 9)
    c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")
    y_position = height - inch

    styles = getSampleStyleSheet()
    keywords_style = styles["Normal"]
    keywords_style.fontName = "Helvetica-Oblique"
    keywords_style.fontSize = 8
    keywords_style.leading = 10
    keywords_style.textColor = colors.darkblue

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
            c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")
            y_position = height - inch
            c.setFont("Helvetica-Bold", 16)
            c.drawString(inch, y_position, "Continued News Report")
            y_position -= 0.4 * inch

        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_position, news['title'])
        y_position -= 0.25 * inch

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
                    c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")
                    y_position = height - inch
                c.drawImage(image, inch, y_position - img_display_height, width=img_display_width, height=img_display_height)
                y_position -= img_display_height + 0.3 * inch
            except Exception as e:
                print(f"Error loading image: {e}")

        c.setFont("Helvetica-Oblique", 11)
        c.drawString(inch, y_position, f"Newspaper: {news['newspaper']}")
        y_position -= 0.25 * inch

        # Draw date/time below newspaper name
        if 'date_time' in news and news['date_time']:
            c.setFont("Helvetica", 10)
            c.drawString(inch, y_position, f"Date/Time: {news['date_time']}")
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
        word_count = len(news['content'].split())
        estimated_minutes = max(1, int(round(word_count / 180)))
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
    c.drawString(width - inch, 0.75 * inch, f"Page {c.getPageNumber()}")

    c.save()
    print(f"PDF generated: {file_name}")


def wrap_text(text, width):
    wrapper = textwrap.TextWrapper(width=width)
    return "\n".join(wrapper.wrap(text))


if __name__ == "__main__":
    with open("scripts/dummy_news.json") as f:
        news_list = json.load(f)
    create_news_pdf("daily_news_report.pdf", news_list)