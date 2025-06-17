import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.report import ReportStatus


class ReportBase(BaseModel):
    search_profile_id: uuid.UUID
    created_at: datetime
    time_slot: Optional[str] = None
    s3_key: str
    status: ReportStatus = ReportStatus.PENDING


class ReportRead(ReportBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    pass


class ReportDetailResponse(ReportRead):
    s3_url: Optional[str] = None


class ReportListResponse(BaseModel):
    reports: List[ReportRead]
