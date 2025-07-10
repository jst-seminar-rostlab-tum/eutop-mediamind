from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class JobStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"

class JobResponse(BaseModel):
    def __init__(self, status: JobStatus, message: str):
        super().__init__(status=status, message=message)

    status: JobStatus = Field(description="Status of the job, can be 'completed' or 'failed'")
    message: str = Field(description="Additional information about the job status")

class PipelineJobRequest(BaseModel):
    start: datetime = Field(
        default_factory=lambda: datetime.combine(datetime.today(), datetime.min.time()),
        description="Start time for the pipeline job, defaults to the start of today")
    end: datetime = Field(
        default_factory=datetime.now,
        description="End time for the pipeline job, defaults to now")
