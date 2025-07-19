from reportlab.platypus import HRFlowable, Paragraph, Spacer
from reportlab.platypus.flowables import AnchorFlowable


def create_summaries_elements(
    news_items, dimensions, translator, styles, pdf_colors
):
    story = []
    for i, news in enumerate(news_items):
        story.append(AnchorFlowable(f"toc_summary_{i}"))
        story.append(
            Paragraph(
                str(i + 1) + ". " + news.title or "",
                styles["newspaper_style"],
            )
        )
        story.append(Spacer(1, 0.05 * dimensions[1] / 11.69))
        story.append(
            Paragraph(
                f'<link href="{news.url}">{news.newspaper.name}</link>' or "",
                styles["keywords_style"],
            )
        )
        story.append(Paragraph(news.published_at, styles["date_style"]))
        story.append(Spacer(1, 0.05 * dimensions[1] / 11.69))
        summary_text = news.summary.replace("\n", "<br/>")
        story.append(Paragraph(summary_text, styles["summary_style"]))
        story.append(Spacer(1, 0.05 * dimensions[1] / 11.69))
        dest_name = f"full_{news.id}"
        story.append(
            Paragraph(
                f"<a href='#{dest_name}'>"
                f"{translator('Read full article')}</a>",
                styles["link_style"],
            )
        )
        if i != len(news_items) - 1:
            story.append(
                HRFlowable(width="100%", thickness=1, color=pdf_colors["main"])
            )
            story.append(Spacer(1, 0.1 * dimensions[1] / 11.69))
    return story
