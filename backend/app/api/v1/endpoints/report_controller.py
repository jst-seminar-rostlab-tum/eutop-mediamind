from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models.user import User
from app.services.report_service import ReportService
from app.services.s3_service import S3Service
from app.services.search_profiles_service import SearchProfileService
from app.schemas.report_schemas import (
    ReportDetailResponse,
    ReportListResponse,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_authenticated_user)],
)

logger = get_logger(__name__)


@router.get("/{search_profile_id}/reports", response_model=ReportListResponse)
async def get_reports(
    search_profile_id: UUID,
    current_user: User = Depends(get_authenticated_user),
):
    profile = await SearchProfileService.get_search_profile_by_id(
        search_profile_id, current_user
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Search profile not found")

    reports = await ReportService.get_reports_by_search_profile(
        search_profile_id
    )
    if not reports:
        raise HTTPException(
            status_code=404, detail="No reports found for this profile"
        )

    return ReportListResponse(reports=reports)


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report_by_id(report_id: UUID):
    report = await ReportService.get_report_by_id(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    # Generate a new presigned S3 URL for the report file
    if report.s3_key:
        presigned_url = S3Service.generate_presigned_url(
            key=report.s3_key, expires_in=604800  # 7 days
        )
    else:
        presigned_url = None

    # Convert to Pydantic model and add s3_url
    response = ReportDetailResponse.model_validate(report)
    response.s3_url = presigned_url
    return response
