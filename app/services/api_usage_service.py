from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.api_usage import ApiUsage
from app.repositories.api_usage_repo import ApiUsageRepository

api_usage_repository = ApiUsageRepository()


def _serialize_usage_record(usage: ApiUsage) -> dict:
    return {
        "id": str(usage.id),
        "user_id": str(usage.user_id) if usage.user_id else None,
        "api_key_id": str(usage.api_key_id) if usage.api_key_id else None,
        "endpoint": usage.endpoint,
        "method": usage.method,
        "operation": usage.operation,
        "algorithm": usage.algorithm,
        "response_status": usage.response_status,
        "response_time_ms": usage.response_time_ms,
        "success": usage.success,
        "ip_address": usage.ip_address,
        "user_agent": usage.user_agent,
        "error_type": usage.error_type,
        "created_at": usage.created_at.isoformat() if usage.created_at else None,
    }


def record_api_usage(
    endpoint: str,
    method: str,
    response_status: int,
    user_id: str | None = None,
    api_key_id: str | None = None,
    operation: str | None = None,
    algorithm: str | None = None,
    response_time_ms: int | None = None,
    success: bool = True,
    ip_address: str | None = None,
    user_agent: str | None = None,
    error_type: str | None = None,
) -> dict:
    if not endpoint or not endpoint.strip():
        raise HTTPException(status_code=400, detail="endpoint is required")
    if not method or not method.strip():
        raise HTTPException(status_code=400, detail="method is required")
    if response_status is None:
        raise HTTPException(status_code=400, detail="response_status is required")

    db = SessionLocal()
    try:
        usage = api_usage_repository.create(
            db,
            {
                "id": uuid4(),
                "user_id": user_id,
                "api_key_id": api_key_id,
                "endpoint": endpoint.strip(),
                "method": method.strip().upper(),
                "operation": operation,
                "algorithm": algorithm,
                "response_status": int(response_status),
                "response_time_ms": response_time_ms,
                "success": success,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "error_type": error_type,
            },
        )
        return _serialize_usage_record(usage)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record API usage") from exc
    finally:
        db.close()


def get_user_usage_summary(user_id: str) -> dict:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    db = SessionLocal()
    try:
        usage_records = api_usage_repository.get_by_user_id(db, user_id)
        total_requests = len(usage_records)
        successful_requests = sum(1 for item in usage_records if item.success)
        failed_requests = total_requests - successful_requests
        success_rate = round((successful_requests / total_requests) * 100, 2) if total_requests else 0.0

        endpoint_breakdown = {}
        for item in usage_records:
            endpoint_breakdown[item.endpoint] = endpoint_breakdown.get(item.endpoint, 0) + 1

        return {
            "user_id": user_id,
            "request_count": total_requests,
            "success_count": successful_requests,
            "failure_count": failed_requests,
            "success_rate": success_rate,
            "endpoint_breakdown": endpoint_breakdown,
        }
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch usage summary") from exc
    finally:
        db.close()


def get_user_usage_records(user_id: str) -> list[dict]:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    db = SessionLocal()
    try:
        usage_records = api_usage_repository.get_by_user_id(db, user_id)
        return [_serialize_usage_record(item) for item in usage_records]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch usage records") from exc
    finally:
        db.close()


def get_recent_usage_activity(user_id: str, limit: int = 10) -> list[dict]:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be greater than 0")

    db = SessionLocal()
    try:
        usage_records = api_usage_repository.get_recent_by_user_id(db, user_id, limit=limit)
        return [_serialize_usage_record(item) for item in usage_records]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch recent usage activity") from exc
    finally:
        db.close()