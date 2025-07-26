from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.schemas.report_schemas import ReportDetailResponse
from app.schemas.user_schema import UserEntity
from app.services.report_service import ReportService
from app.services.s3_service import (
    S3Service,
    get_s3_service,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_authenticated_user)],
)

logger = get_logger(__name__)


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report_by_id(
    report_id: UUID,
    s3_service: S3Service = Depends(get_s3_service),
    current_user: UserEntity = Depends(get_authenticated_user),
):
    report = await ReportService.get_report_by_id(report_id)
    if report is None:
        logger.warning(f"Report not found for id: {report_id}")
        raise HTTPException(status_code=404, detail="Report not found")

    presigned_url = None
    if not report.s3_key:
        logger.error(f"Report {report.id} has no s3_key set.")
    else:
        try:
            presigned_url = s3_service.generate_presigned_url(
                key=report.s3_key, expires_in=604800
            )
        except Exception as e:
            logger.error(
                f"Failed to generate presigned URL for report {report.id}: {e}"
            )

    response = ReportDetailResponse.model_validate(
        report, from_attributes=True
    )
    response.s3_url = presigned_url
    return response
