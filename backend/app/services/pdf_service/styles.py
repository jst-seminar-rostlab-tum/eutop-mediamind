# This file contains all paragraph and table styles for the PDF service.
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle

from .colors import pdf_colors

# Font registration will be handled in the main PDFService class


def get_pdf_styles(fonts_registered: bool):
    return {
        "link_style": ParagraphStyle(
            "Link",
            fontName=(
                "DVS-BoldOblique"
                if fonts_registered
                else "Helvetica-BoldOblique"
            ),
            fontSize=8,
            textColor=pdf_colors["electricBlue"],
            spaceAfter=6,
            bulletIndent=0,
            leftIndent=6,
            leading=12,
            alignment=TA_JUSTIFY,
        ),
        "button_style": ParagraphStyle(
            "Link",
            fontName=("DVS-Bold" if fonts_registered else "Helvetica-Bold"),
            fontSize=8,
            textColor=pdf_colors["electricBlue"],
            spaceAfter=6,
            bulletIndent=0,
            leftIndent=6,
            leading=12,
            alignment=TA_JUSTIFY,
        ),
        "newspaper_style": ParagraphStyle(
            "Newspaper",
            fontName="DVS-Bold" if fonts_registered else "Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=pdf_colors["main"],
        ),
        "keywords_style": ParagraphStyle(
            "Keywords",
            fontName=(
                "DVS-Oblique" if fonts_registered else "Helvetica-Oblique"
            ),
            fontSize=8,
            leading=10,
            textColor=pdf_colors["blue"],
        ),
        "date_style": ParagraphStyle(
            "Date",
            fontName=(
                "DVS-Oblique" if fonts_registered else "Helvetica-Oblique"
            ),
            fontSize=8,
            leading=10,
            textColor=pdf_colors["gray"],
        ),
        "summary_style": ParagraphStyle(
            "Summary",
            fontName="DVS",
            fontSize=9,
            leading=12,
            alignment=TA_JUSTIFY,
        ),
        "title_style": ParagraphStyle(
            "Title",
            fontName="DVS-Bold",
            fontSize=18,
            leading=20,
            spaceAfter=12,
            textColor=pdf_colors["main"],
        ),
        "subtitle_style": ParagraphStyle(
            "Title",
            fontName="DVS-Bold",
            fontSize=14,
            leading=10,
            spaceAfter=10,
        ),
        "metadata_style": ParagraphStyle(
            "Metadata",
            fontName="DVS" if fonts_registered else "Helvetica-Oblique",
            fontSize=8,
            leading=12,
            textColor=pdf_colors["gray"],
        ),
        "metadata_title_style": ParagraphStyle(
            "Metadata_title",
            fontName=(
                "DVS-BoldOblique" if fonts_registered else "Helvetica-Oblique"
            ),
            fontSize=8,
            leading=12,
            textColor=pdf_colors["gray"],
        ),
        "metadata_subtitle_style": ParagraphStyle(
            "Metadata_subtitle",
            fontName=(
                "DVS-BoldOblique" if fonts_registered else "Helvetica-Oblique"
            ),
            fontSize=8,
            leading=12,
            textColor=pdf_colors["gray"],
        ),
        "content_style": ParagraphStyle(
            "Content",
            fontName="DVS",
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
        ),
        "reading_time_style": ParagraphStyle(
            "ReadingTime",
            fontName="DVS" if fonts_registered else "Helvetica",
            fontSize=12,
            textColor=pdf_colors["darkgreen"],
            allowOrphans=0,
            allowWidows=0,
        ),
        "reading_time_bold_style": ParagraphStyle(
            "ReadingTimeBold",
            parent=None,  # Set parent in main class if needed
            fontName="DVS-Bold" if fonts_registered else "Helvetica-Bold",
        ),
    }
