# This file contains the font registration logic for the PDF service.
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

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
        "DVS": "DejaVuSans.ttf",
        "DVS-Bold": "DejaVuSans-Bold.ttf",
        "DVS-Oblique": "DejaVuSans-Oblique.ttf",
        "DVS-BoldOblique": "DejaVuSans-BoldOblique.ttf",
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
    #Add Mapping converts the html <bold> <italic> tags to the font styles
    addMapping("DVS", 0, 0, "DVS")
    addMapping("DVS", 1, 0, "DVS-Bold")
    addMapping("DVS", 0, 1, "DVS-Oblique")
    addMapping("DVS", 1, 1, "DVS-BoldOblique")
    return True
