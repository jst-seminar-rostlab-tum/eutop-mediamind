from sqlalchemy import Column, Integer, String, Boolean
from backend.db.session import Base

class NewspaperSource(Base):
    __tablename__ = "newspaper_sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    scraper_type = Column(String, nullable=False)
    # Zusätzliche Felder als JSON-String
    config = Column(String, nullable=True)
    login_required = Column(Boolean, default=False)
