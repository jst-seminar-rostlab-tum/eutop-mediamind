from typing import Literal

from pydantic import BaseModel, Field


class MatchFeedbackRequest(BaseModel):
    comment: str
    reason: Literal["bad source", "false", "no good matching", "other"]
    ranking: int = Field()
