from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.schemas.report_schemas import ReportDetailResponse
from app.services.report_service import ReportService
from app.services.s3_service import S3Service

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_authenticated_user)],
)

logger = get_logger(__name__)


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report_by_id(report_id: UUID):
    report = await ReportService.get_report_by_id(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    presigned_url = (
        S3Service.generate_presigned_url(key=report.s3_key, expires_in=604800)
        if report.s3_key
        else None
    )

    response = ReportDetailResponse.model_validate(
        report, from_attributes=True
    )
    response.s3_url = presigned_url
    return response
