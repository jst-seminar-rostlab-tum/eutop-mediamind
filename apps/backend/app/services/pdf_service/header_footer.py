from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle

from .colors import pdf_colors


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
            Paragraph(f"<b>{translator('Current Press Report')}</b>", style),
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
