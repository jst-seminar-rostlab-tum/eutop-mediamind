from datetime import date
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from models import Article

class PDFService:

    @staticmethod
    def create_pdf(articles: List[Article]) -> BytesIO:
        toc_entries = []
        temp_buffer = BytesIO()
        temp_canvas = canvas.Canvas(temp_buffer, pagesize=A4)

        # Start after front and TOC pages
        page_counter = 2

        for article in articles:
            toc_entries.append((article.title, page_counter))
            draw_article_page(temp_canvas, article)
            temp_canvas.showPage()
            page_counter += 1

        temp_canvas.save()

        out_buffer = BytesIO()
        c = canvas.Canvas(out_buffer, pagesize=A4)

        today = date.ctime(date.today()).format("%d.%m.%Y")
        draw_front_page(c, "Pressespiegel", "Erstellt am " + today + "\n" + str(len(articles)) + " Artikel")
        c.showPage()

        draw_table_of_contents(c, toc_entries)
        c.showPage()

        for article in articles:
            draw_article_page(c, article)
            c.showPage()

        c.save()
        return out_buffer

    @staticmethod
    def draw_front_page(c :canvas.Canvas, title: str, subtitle: str):
        from datetime import datetime
        width, height = A4
        margin = 50

        # Background color (optional)
        c.setFillColorRGB(0.95, 0.95, 1)
        c.rect(0, 0, width, height, fill=1)

        # Title
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.darkblue)
        c.drawCentredString(width / 2, height - 150, title)

        # Subtitle
        c.setFont("Helvetica-Oblique", 16)
        c.setFillColor(colors.grey)
        c.drawCentredString(width / 2, height - 190, subtitle)

        # Decorative line
        c.setStrokeColor(colors.lightblue)
        c.setLineWidth(2)
        c.line(margin, height - 210, width - margin, height - 210)

        # Date at bottom
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        date_str = datetime.today().strftime("%B %d, %Y")
        c.drawCentredString(width / 2, 100, f"Generated on {date_str}")

    @staticmethod
    def draw_table_of_contents(c: canvas.Canvas, toc_entries):
        width, height = A4
        margin = 70

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height - 100, "Table of Contents")

        y = height - 140
        c.setFont("Helvetica", 12)

        for title, page in toc_entries:
            if y < 100:
                c.showPage()
                y = height - 100
            c.drawString(margin, y, f"{title}")
            c.drawRightString(width - margin, y, f"Page {page}")
            y -= 20

    @staticmethod
    def draw_article_page(c: canvas.Canvas, article: Article):
        width, height = A4
        margin = 50
        line_y = height - 100

        # Title
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(colors.darkblue)
        c.drawCentredString(width / 2, height - 80, article.title)

        # Date
        c.setFont("Helvetica-Oblique", 12)
        c.setFillColor(colors.grey)

        # Decorative line
        c.setStrokeColor(colors.darkblue)
        c.setLineWidth(1)
        c.line(margin, line_y - 40, width - margin, line_y - 40)

        # Summary text block
        text = c.beginText(margin, line_y - 80)
        text.setFont("Helvetica", 12)
        text.setFillColor(colors.black)

        # Wrap summary text nicely
        if article.summary != None:
            for line in article.summary.split('\n'):
                for segment in self.split_paragraph(line, 90):  # wrap at 90 chars
                    text.textLine(segment)
                text.textLine('')  # extra line between paragraphs

        c.drawText(text)

    @staticmethod
    def split_paragraph(text: str, max_chars=90) -> List[str]:
        """Wrap a string into lines of at most max_chars."""
        words = text.split()
        lines = []
        line = ''
        for word in words:
            if len(line + ' ' + word) <= max_chars:
                line += (' ' if line else '') + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

