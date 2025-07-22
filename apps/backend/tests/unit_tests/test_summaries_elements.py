# 1%
from app.services.pdf_service import summaries_elements
from reportlab.lib.styles import getSampleStyleSheet

class DummyNews:
    def __init__(self):
        self.title = 'title'
        self.url = 'http://test.com'
        self.newspaper = type('np', (), {'name': 'np'})()
        self.summary = 'summary'
        self.published_at = '2025-01-01'
        self.id = 1

def test_create_summaries_elements():
    news_items = [DummyNews()]
    dimensions = (100, 100)
    translator = lambda x: x
    # use the sample styles from ReportLab
    sample_styles = getSampleStyleSheet()
    styles = {
        "newspaper_style": sample_styles["Normal"],
        "keywords_style": sample_styles["Normal"],
        "date_style": sample_styles["Normal"],
        "summary_style": sample_styles["Normal"],
        "link_style": sample_styles["Normal"],
    }
    pdf_colors = {"main": "black"}
    elements = summaries_elements.create_summaries_elements(news_items, dimensions, translator, styles, pdf_colors)
    assert isinstance(elements, list)
