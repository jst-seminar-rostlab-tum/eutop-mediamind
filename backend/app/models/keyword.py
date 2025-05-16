from sqlmodel import SQLModel, Field

import uuid
class Keyword(SQLModel):
    __tablename__ = "keywords"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
