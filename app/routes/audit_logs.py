from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class AuditLog(BaseModel):
    id: str
    action: str
    user_id: str
    timestamp: str
    details: str

MOCK_AUDIT_LOGS = [
    AuditLog(
        id="log-001",
        action="kem_encapsulate",
        user_id="mock-user",
        timestamp="2026-06-10T10:00:00",
        details="KEM encapsulation performed with ML-KEM-768"
    ),
    AuditLog(
        id="log-002",
        action="sign",
        user_id="mock-user",
        timestamp="2026-06-10T11:00:00",
        details="Message signed with ML-DSA-65"
    ),
    AuditLog(
        id="log-003",
        action="verify",
        user_id="mock-user",
        timestamp="2026-06-10T12:00:00",
        details="Signature verified with ML-DSA-65"
    ),
]

@router.get(
    "/audit-logs",
    response_model=List[AuditLog],
    summary="Get Audit Logs",
    description="Returns all audit logs."
)
def get_audit_logs():
    return MOCK_AUDIT_LOGS