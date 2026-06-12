from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

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

MOCK_AUDIT_LOGS = [
    AuditLog(
        id="log-001",
        timestamp="2026-06-10T10:00:00",
        eventType="KEM Encapsulation",
        algorithm="ML-KEM-768",
        keyId="key_mlkem_84f9b2d3c1a9",
        status="Success",
        details="KEM encapsulation performed with ML-KEM-768",
        ipAddress="192.168.1.100",
        user="Admin"
    ),
    AuditLog(
        id="log-002",
        timestamp="2026-06-10T11:00:00",
        eventType="Signature Generation",
        algorithm="ML-DSA-65",
        keyId="key_mldsa_2b810d7a314b",
        status="Success",
        details="Message signed with ML-DSA-65",
        ipAddress="192.168.1.100",
        user="Admin"
    ),
    AuditLog(
        id="log-003",
        timestamp="2026-06-10T12:00:00",
        eventType="Signature Verification",
        algorithm="ML-DSA-65",
        keyId="key_mldsa_2b810d7a314b",
        status="Success",
        details="Signature verified with ML-DSA-65",
        ipAddress="192.168.1.100",
        user="Admin"
    ),
    AuditLog(
        id="log-004",
        timestamp="2026-06-10T13:00:00",
        eventType="Key Generation",
        algorithm="ML-KEM-1024",
        keyId="key_mlkem_1024_deadbeef",
        status="Success",
        details="Quantum-safe root encryption key generated in HSM enclave.",
        ipAddress="192.168.1.100",
        user="Admin"
    ),
    AuditLog(
        id="log-005",
        timestamp="2026-06-10T14:00:00",
        eventType="Key Revocation",
        algorithm="ML-KEM-512",
        keyId="key_mlkem_512_expired",
        status="Success",
        details="Revoked legacy Level 1 key due to corporate policy upgrade.",
        ipAddress="192.168.1.100",
        user="SecOps Daemon"
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