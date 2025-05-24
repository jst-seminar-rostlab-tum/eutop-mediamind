from pydantic import BaseModel, Field
from typing import Literal


class MatchFeedbackRequest(BaseModel):
    comment: str
    reason: Literal["bad source", "false", "no good matching", "other"]
    ranking: int = Field()
