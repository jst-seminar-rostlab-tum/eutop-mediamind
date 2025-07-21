# This file contains the font registration logic for the PDF service.
import os

from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.logger import get_logger

logger = get_logger(__name__)


def register_fonts():
    font_dir = "assets/fonts"
    if not os.path.exists(font_dir):
        logger.warning(
            f"Font directory '{font_dir}' not found. Using default fonts."
        )
        return False
    fonts = {
        "Regular": "Inter_18pt-Regular.ttf",
        "Bold": "Inter_18pt-Bold.ttf",
        "Oblique": "Inter_18pt-Italic.ttf",
        "BoldOblique": "Inter_18pt-BoldItalic.ttf",
    }
    for font_name, file_name in fonts.items():
        font_path = os.path.join(font_dir, file_name)
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        else:
            logger.warning(
                f"Font file '{font_path}' not found. Some styles may "
                f"not display correctly."
            )
    # Add Mapping converts the html <bold> <italic> tags to the font styles
    addMapping("Regular", 0, 0, "Regular")
    addMapping("Regular", 1, 0, "Bold")
    addMapping("Regular", 0, 1, "Oblique")
    addMapping("Regular", 1, 1, "BoldOblique")
    return True
