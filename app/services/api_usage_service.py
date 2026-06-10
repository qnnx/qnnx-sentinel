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
        "actor_id": str(usage.actor_id) if usage.actor_id else None,
        "endpoint": usage.endpoint,
        "http_method": usage.http_method,
        "algorithm": usage.algorithm,
        "response_status": usage.response_status,
        "response_time_ms": usage.response_time_ms,
        "request_count": usage.request_count,
        "created_at": usage.created_at.isoformat() if usage.created_at else None,
    }


def record_api_usage(
    endpoint: str,
    http_method: str,
    response_status: int,
    actor_id: str | None = None,
    algorithm: str | None = None,
    response_time_ms: int | None = None,
) -> dict:
    if not endpoint or not endpoint.strip():
        raise HTTPException(status_code=400, detail="endpoint is required")
    if not http_method or not http_method.strip():
        raise HTTPException(status_code=400, detail="http_method is required")
    if response_status is None:
        raise HTTPException(status_code=400, detail="response_status is required")

    db = SessionLocal()
    try:
        usage = api_usage_repository.create(
            db,
            {
                "id": uuid4(),
                "actor_id": actor_id,
                "endpoint": endpoint.strip(),
                "http_method": http_method.strip().upper(),
                "algorithm": algorithm,
                "response_status": int(response_status),
                "response_time_ms": response_time_ms,
                "request_count": 1,
            },
        )
        return _serialize_usage_record(usage)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record API usage") from exc
    finally:
        db.close()


def get_user_usage_summary(actor_id: str) -> dict:
    if not actor_id:
        raise HTTPException(status_code=400, detail="actor_id is required")

    db = SessionLocal()
    try:
        usage_records = api_usage_repository.get_by_actor_id(db, actor_id)
        total_requests = len(usage_records)
        successful_requests = sum(1 for item in usage_records if 200 <= item.response_status < 400)
        failed_requests = total_requests - successful_requests
        success_rate = round((successful_requests / total_requests) * 100, 2) if total_requests else 0.0

        endpoint_breakdown = {}
        for item in usage_records:
            endpoint_breakdown[item.endpoint] = endpoint_breakdown.get(item.endpoint, 0) + 1

        return {
            "actor_id": actor_id,
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


def get_recent_usage_activity(actor_id: str, limit: int = 10) -> list[dict]:
    if not actor_id:
        raise HTTPException(status_code=400, detail="actor_id is required")
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be greater than 0")

    db = SessionLocal()
    try:
        usage_records = api_usage_repository.get_recent_by_actor_id(db, actor_id, limit=limit)
        return [_serialize_usage_record(item) for item in usage_records]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch recent usage activity") from exc
    finally:
        db.close()