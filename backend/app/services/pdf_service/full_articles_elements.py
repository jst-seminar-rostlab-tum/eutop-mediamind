from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import AnchorFlowable

from .colors import pdf_colors
from .markdown_utils import markdown_blocks_to_paragraphs
from .utils import calculate_reading_time


def create_full_articles_elements(news_items, dimensions, translator, styles):
    story = []
    for i, news in enumerate(news_items):
        dest_name = f"full_{news.id}"
        story.append(AnchorFlowable(dest_name))
        story.append(AnchorFlowable(f"toc_article_{i}"))
        story.append(
            Paragraph(
                str(i + 1) + ". " + news.title,
                styles["title_style"],
            )
        )

        # Wrap metadata in a styled table box
        metadata_text = f"""
        {translator('Published at')}: {news.published_at} |
         {translator('Newspaper')}: {news.newspaper.name}
                """
        metadata_para = Paragraph(metadata_text, styles["metadata_style"])
        metadata_first = Table(
            [[metadata_para]],
            colWidths=[dimensions[0] - 2 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), pdf_colors["white"]),
                    ("BOX", (0, 0), (-1, -1), 0.25, pdf_colors["white"]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            ),
        )
        story.append(metadata_first)

        # Summary
        story.append(
            Paragraph(
                translator("Summary"),
                styles["subtitle_style"],
            )
        )
        story.append(Paragraph(news.summary, styles["content_style"]))
        story.append(Spacer(1, 0.15 * inch))

        story.append(
            Paragraph(
                translator("Article Content"),
                styles["subtitle_style"],
            )
        )

        # Calculate reading time
        reading_time = calculate_reading_time(news.content)
        reading_time_text = (
            f"{translator('Estimated Reading Time')}: "
            f"{reading_time} {translator('min')}"
        )
        reading_time_para = Paragraph(reading_time_text, styles["link_style"])
        read_summary_para = Paragraph(
            f"""
            <para alignment=\"right\">\n
                <a href=\"#toc_summary_{i}\">\n
                <u><font>{translator('Back to Summary List')}</font></u>\n
                </a>\n
            </para>
            """,
            styles["link_style"],
        )
        # Put reading time and read summary in a box
        reading_time_box = Table(
            [[reading_time_para, read_summary_para]],
            colWidths=[
                2.5 * inch,
                (dimensions[0] - 2 * inch - 2.5 * inch),
            ],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), pdf_colors["white"]),
                    ("BOX", (0, 0), (-1, -1), 0.25, pdf_colors["white"]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            ),
        )
        story.append(reading_time_box)

        # Translating Content Markdown to Reportlab Paragraphs
        for para in markdown_blocks_to_paragraphs(news.content, styles):
            story.append(para)
        story.append(Spacer(1, 0.3 * inch))

        # Metadata Box
        word_count = len(news.content.split()) if news.content else 0
        persons_str = ", ".join(f"{p}" for p in news.persons)
        organizations_str = ", ".join(f"{i}" for i in news.organizations)
        industries_str = ", ".join(f"{i}" for i in news.industries)
        events_str = ", ".join(f"{i}" for i in news.events)

        # Prepare metadata as label-value pairs for two columns
        metadata_rows = [
            [
                Paragraph(
                    f"{translator('Words')}:",
                    styles["metadata_style"],
                ),
                Paragraph(str(word_count), styles["metadata_style"]),
            ],
            [
                Paragraph(
                    f"{translator('Reading Time')}:",
                    styles["metadata_style"],
                ),
                Paragraph(
                    f"{reading_time} {translator('min')}",
                    styles["metadata_style"],
                ),
            ],
            [
                Paragraph(
                    f"{translator('Author')}:",
                    styles["metadata_style"],
                ),
                Paragraph(news.author, styles["metadata_style"]),
            ],
            [
                Paragraph(
                    f"{translator('Newspaper')}:",
                    styles["metadata_style"],
                ),
                Paragraph(
                    news.newspaper.name,
                    styles["metadata_style"],
                ),
            ],
            [
                Paragraph(
                    f"<b>{translator('Published at')}:</b>",
                    styles["metadata_style"],
                ),
                Paragraph(news.published_at, styles["metadata_style"]),
            ],
            [
                Paragraph(
                    f"<b>{translator('Language')}:</b>",
                    styles["metadata_style"],
                ),
                Paragraph(
                    news.language or translator("Unknown"),
                    styles["metadata_style"],
                ),
            ],
            [
                Paragraph(
                    f"<b>{translator('Category')}:</b>",
                    styles["metadata_style"],
                ),
                Paragraph(
                    news.category or translator("Unknown"),
                    styles["metadata_style"],
                ),
            ],
            [
                Paragraph(
                    f"<b>{translator('Keywords')}:</b>",
                    styles["metadata_style"],
                ),
                Paragraph(
                    (
                        ", ".join(news.keywords)
                        if news.keywords
                        else translator("None")
                    ),
                    styles["metadata_style"],
                ),
            ],
            [
                Paragraph(
                    f"<b>{translator('Mentioned in this article')}:</b>",
                    styles["metadata_subtitle_style"],
                ),
                "",
            ],
            [
                Paragraph(
                    f"<b>{translator('People')}:</b>",
                    styles["metadata_style"],
                ),
                Paragraph(
                    persons_str if persons_str else translator("None"),
                    styles["metadata_style"],
                ),
            ],
            [
                Paragraph(
                    f"<b>{translator('Organizations')}:</b>",
                    styles["metadata_style"],
                ),
                Paragraph(
                    (
                        organizations_str
                        if organizations_str
                        else translator("None")
                    ),
                    styles["metadata_style"],
                ),
            ],
            [
                Paragraph(
                    f"<b>{translator('Industries')}:</b>",
                    styles["metadata_style"],
                ),
                Paragraph(
                    (industries_str if industries_str else translator("None")),
                    styles["metadata_style"],
                ),
            ],
            [
                Paragraph(
                    f"<b>{translator('Events')}:</b>",
                    styles["metadata_style"],
                ),
                Paragraph(
                    events_str if events_str else translator("None"),
                    styles["metadata_style"],
                ),
            ],
        ]

        combined_box = Table(
            metadata_rows,
            colWidths=[
                (dimensions[0] - 4 * inch) * 0.25,
                (dimensions[0] - 1.5 * inch) * 0.75,
            ],
            style=TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        pdf_colors["whitesmoke"],
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.25,
                        pdf_colors["lightgrey"],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    (
                        "SPAN",
                        (0, 8),
                        (1, 8),
                    ),  # Span both columns for "Mentioned in this article"
                ]
            ),
        )
        story.append(combined_box)
        story.append(Spacer(1, 0.1 * inch))

        # URL Link Button
        link_img = Image("assets/link_icon.png", width=16, height=16)
        button = Table(
            [
                [
                    link_img,
                    Paragraph(
                        f'<a href="{news.url}">'
                        f'<b>{translator("Read Article at Newspaper")}'
                        f"</b></a>",
                        styles["link_style"],
                    ),
                ]
            ],
            colWidths=[0.2 * inch, 2.1 * inch],
            hAlign="RIGHT",
        )
        button.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), pdf_colors["white"]),
                    ("TEXTCOLOR", (0, 0), (-1, -1), pdf_colors["blue"]),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("INNERGRID", (0, 0), (-1, -1), 0, pdf_colors["white"]),
                    ("BOX", (0, 0), (-1, -1), 1, pdf_colors["white"]),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        story.append(button)

        if i != len(news_items) - 1:
            story.append(PageBreak())
    return story
