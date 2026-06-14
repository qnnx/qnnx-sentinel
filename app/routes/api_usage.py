import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_current_user
from app.schemas.api_usage import ApiUsageResponse, ApiUsageSummaryResponse
from app.services.api_usage_service import (
    get_recent_usage_activity,
    get_user_usage_records,
    get_user_usage_summary,
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/api-usage",
    response_model=list[ApiUsageResponse],
    summary="Get API Usage",
    description="Returns API usage records for the authenticated user."
)
def get_usage(current_user=Depends(get_current_user)):
    try:
        usage_records = get_user_usage_records(current_user["id"])
        return [ApiUsageResponse(**record) for record in usage_records]
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch API usage")
        raise HTTPException(status_code=500, detail="Failed to fetch API usage") from exc


@router.get(
    "/api-usage/recent",
    response_model=list[ApiUsageResponse],
    summary="Get Recent API Usage",
    description="Returns recent API usage records for the authenticated user."
)
def get_recent_usage(limit: int = Query(10, ge=1, le=100), current_user=Depends(get_current_user)):
    try:
        usage_records = get_recent_usage_activity(current_user["id"], limit=limit)
        return [ApiUsageResponse(**record) for record in usage_records]
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch recent API usage")
        raise HTTPException(status_code=500, detail="Failed to fetch recent API usage") from exc


@router.get(
    "/api-usage/summary",
    response_model=ApiUsageSummaryResponse,
    summary="Get API Usage Summary",
    description="Returns an API usage summary for the authenticated user."
)
def get_usage_summary(current_user=Depends(get_current_user)):
    try:
        summary = get_user_usage_summary(current_user["id"])
        return ApiUsageSummaryResponse(**summary)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch API usage summary")
        raise HTTPException(status_code=500, detail="Failed to fetch API usage summary") from exc
