from datetime import datetime

from sqlmodel import SQLModel, Field

import uuid
class Subscription(SQLModel):
    __tablename__ = "subscriptions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    domain: str = Field(max_length=255)
    vault_path: str = Field(max_length=255)
    config: str = Field(max_length=255)
    scraper_type: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)


