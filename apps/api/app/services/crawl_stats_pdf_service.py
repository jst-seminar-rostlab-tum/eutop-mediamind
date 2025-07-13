import asyncio
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.repositories.crawl_stats_repository import CrawlStatsRepository


# The PDF is stored inside the backend directory
async def generate_crawl_stats_pdf(filename: str = "crawl_stats_report.pdf"):
    # Fetch crawl stats for the last day
    crawl_stats = await CrawlStatsRepository.get_crawl_stats_last_day()

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"].clone("normal_style")
    normal_style.fontSize = 7
    normal_style.leading = 9
    normal_style.wordWrap = "CJK"
    # Use a smaller custom style for the header
    header_style = styles["Normal"].clone("header_style")
    header_style.fontSize = 7
    header_style.leading = 9
    header_style.alignment = 1  # Center
    header_style.wordWrap = "CJK"

    # Prepare table data with Paragraphs for wrapping
    data = [
        [
            Paragraph("Subscription", header_style),
            Paragraph("Total Successful", header_style),
            Paragraph("Total Attempted", header_style),
            Paragraph("Notes", header_style),
        ]
    ]
    for stat in crawl_stats:
        # If no subscription name is set, use the subscription ID
        subscription_name = getattr(stat, "subscription_name", None)
        if (
            not subscription_name
            and hasattr(stat, "subscription")
            and hasattr(stat.subscription, "name")
        ):
            subscription_name = stat.subscription.name
        if not subscription_name:
            subscription_name = str(stat.subscription_id)
        data.append(
            [
                Paragraph(subscription_name, normal_style),
                Paragraph(str(stat.total_successful), normal_style),
                Paragraph(str(stat.total_attempted), normal_style),
                Paragraph(stat.notes[:5000] or "", normal_style),
            ]
        )

    # Create Stats PDF
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(
        Paragraph("Crawl Stats Report (Last 24h)", styles["Title"])
    )
    elements.append(
        Paragraph(
            f"{datetime.today().strftime('%d %B %Y - %H:%M')}", styles["Title"]
        )
    )
    elements.append(Spacer(1, 12))
    # Margins of the PDF to fit the table
    page_width = A4[0] - doc.leftMargin / 2 - doc.rightMargin / 2
    # The widths of each column to try to always fit one line per subscription
    col_widths = [
        page_width * 0.30,
        page_width * 0.13,
        page_width * 0.13,
        page_width * 0.42,
    ]
    table = Table(data, repeatRows=1, colWidths=col_widths, splitByRow=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)


if __name__ == "__main__":
    asyncio.run(generate_crawl_stats_pdf())
