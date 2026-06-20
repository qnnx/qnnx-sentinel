import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.schemas.audit_logs import AuditLogResponse
from app.services.audit_log_service import get_audit_log_by_id, get_user_audit_logs

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/audit-logs",
    response_model=list[AuditLogResponse],
    summary="Get Audit Logs",
    description="Returns all audit logs for the authenticated user."
)
def get_audit_logs(current_user=Depends(get_current_user)):
    logs = get_user_audit_logs(current_user["id"])
    return [AuditLogResponse(**log) for log in logs]


@router.get(
    "/audit-logs/{log_id}",
    response_model=AuditLogResponse,
    summary="Get Audit Log By ID",
    description="Returns a single audit log for the authenticated user."
)
def get_audit_log(log_id: UUID, current_user=Depends(get_current_user)):
    log = get_audit_log_by_id(current_user["id"], str(log_id))
    return AuditLogResponse(**log)
