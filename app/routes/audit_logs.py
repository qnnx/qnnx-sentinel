from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.core.supabase_client import supabase

router = APIRouter()

class AuditLog(BaseModel):
    id: str
    timestamp: str
    eventType: str
    algorithm: str
    keyId: str
    status: str
    details: str
    ipAddress: str
    user: str

@router.get(
    "/audit-logs",
    response_model=List[AuditLog],
    summary="Get Audit Logs",
    description="Returns all audit logs from Supabase."
)
def get_audit_logs():
    try:
        response = supabase.table("audit_logs").select("*").order("timestamp", desc=True).execute()
        logs = []
        for row in response.data:
            logs.append(AuditLog(
                id=row["id"],
                timestamp=row["timestamp"],
                eventType=row["event_type"],
                algorithm=row["algorithm"] or "",
                keyId=row["key_id"] or "",
                status=row["status"] or "Success",
                details=row["details"] or "",
                ipAddress=row["ip_address"] or "",
                user=row["user_name"] or ""
            ))
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))