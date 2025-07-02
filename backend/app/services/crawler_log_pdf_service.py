from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from app.repositories.crawl_stats_repository import CrawlStatsRepository
import asyncio

async def generate_crawl_stats_pdf(filename: str = "crawl_stats_report.pdf"):
    # Fetch crawl stats for the last day
    crawl_stats = await CrawlStatsRepository.get_crawl_stats_last_day()

    # Prepare table data
    data = [["Subscription Name", "Total Successful", "Total Attempted", "Notes"]]
    for stat in crawl_stats:
        # Try to get subscription name, fallback to ID if not present
        subscription_name = getattr(stat, "subscription_name", None)
        if not subscription_name and hasattr(stat, "subscription") and hasattr(stat.subscription, "name"):
            subscription_name = stat.subscription.name
        if not subscription_name:
            subscription_name = str(stat.subscription_id)
        data.append([
            subscription_name,
            str(stat.total_successful),
            str(stat.total_attempted),
            stat.notes or ""
        ])

    # Create PDF
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Crawl Stats Report (Last 24h)", styles["Title"]))
    elements.append(Paragraph(
        f"{datetime.today().strftime('%d %B %Y - %H:%M')}",
        styles["Title"]
    ))
    elements.append(Spacer(1, 12))
    # Set column widths to use almost all the page width
    page_width = A4[0] - (doc.leftMargin /2) - (doc.rightMargin /2)
    col_widths = [page_width * 0.22, page_width * 0.22, page_width * 0.22, page_width * 0.34]
    table = Table(data, repeatRows=1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

# async def print_crawl_stats_count():
#     # Fetch all crawl stats
#     all_stats = await CrawlStatsRepository.get_crawl_stats_last_day()
#     print(f"Total CrawlStats entries in database: {len(all_stats)}")
#     if all_stats:
#         print("Sample entry:", all_stats[0])
#     else:
#         print("No CrawlStats data found.")

if __name__ == "__main__":
    #asyncio.run(print_crawl_stats_count())
    asyncio.run(generate_crawl_stats_pdf())
