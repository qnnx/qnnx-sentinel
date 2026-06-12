import base64
import binascii
import time
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.repositories.algorithm_repo import AlgorithmRepository
from app.repositories.key_repo import KeyRepository
from app.schemas.api_key import ApiKeyContext
from app.services import dsa_service, kem_service
from app.services.api_usage_service import record_api_usage
from app.services.audit_log_service import create_audit_log

algorithm_repository = AlgorithmRepository()
key_repository = KeyRepository()


def _decode_base64(value: str, field_name: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Base64 for {field_name}") from exc


def _encode_base64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _record_operation(
    *,
    api_key_context: ApiKeyContext,
    endpoint: str,
    method: str,
    operation: str,
    algorithm: str,
    response_status: int,
    success: bool,
    response_time_ms: int,
    audit_action: str,
    audit_status: str,
    details: dict,
    api_key_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    error_type: str | None = None,
):
    try:
        create_audit_log(
            action=audit_action,
            user_id=str(api_key_context.user_id),
            api_key_id=api_key_id or str(api_key_context.id),
            status=audit_status,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
    except HTTPException:
        pass

    try:
        record_api_usage(
            user_id=str(api_key_context.user_id),
            api_key_id=str(api_key_context.id),
            endpoint=endpoint,
            method=method,
            operation=operation,
            algorithm=algorithm,
            response_status=response_status,
            response_time_ms=response_time_ms,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            error_type=error_type,
        )
    except HTTPException:
        pass


def _record_failure(
    *,
    api_key_context: ApiKeyContext,
    endpoint: str,
    method: str,
    operation: str,
    algorithm: str,
    response_status: int,
    response_time_ms: int,
    audit_action: str,
    error_type: str,
    details: dict,
    api_key_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
):
    _record_operation(
        api_key_context=api_key_context,
        endpoint=endpoint,
        method=method,
        operation=operation,
        algorithm=algorithm,
        response_status=response_status,
        success=False,
        response_time_ms=response_time_ms,
        audit_action=audit_action,
        audit_status="failed",
        api_key_id=api_key_id,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type=resource_type,
        resource_id=resource_id,
        error_type=error_type,
        details=details,
    )


def _resolve_algorithm_record(algorithm: str):
    db = SessionLocal()
    try:
        record = algorithm_repository.get_by_identifier(db, algorithm)
        if not record:
            raise HTTPException(status_code=400, detail="Algorithm not found")
        return record
    finally:
        db.close()


def _detect_key_type(algorithm_name: str) -> str:
    normalized = algorithm_name.casefold()
    if "kem" in normalized:
        return "kem"
    if "dsa" in normalized:
        return "signature"
    raise HTTPException(status_code=400, detail=f"Unsupported algorithm family: {algorithm_name}")


def generate_and_store_keypair(
    *,
    api_key_context: ApiKeyContext,
    algorithm: str,
    storage_mode: str,
    endpoint: str,
    method: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    start = time.perf_counter()
    try:
        algorithm_record = _resolve_algorithm_record(algorithm)
        key_type = _detect_key_type(algorithm_record.name)

        if storage_mode == "sentinel_managed":
            raise HTTPException(status_code=501, detail="sentinel_managed storage not implemented yet")

        if key_type == "kem":
            raw_response = kem_service.generate_kem_keypair(algorithm_record.name)
        else:
            raw_response = dsa_service.generate_dsa_keypair(algorithm_record.name)

        db = SessionLocal()
        try:
            key = key_repository.create(
                db,
                {
                    "id": uuid4(),
                    "user_id": api_key_context.user_id,
                    "algorithm_id": algorithm_record.id,
                    "key_type": key_type,
                    "status": "active",
                    "public_key": _encode_base64(raw_response["public_key"]),
                    "private_key_ref": None,
                    "storage_mode": storage_mode,
                    "private_key_exported": True,
                },
            )
        finally:
            db.close()

        response = {
            "key_id": str(key.id),
            "algorithm": raw_response["algorithm"],
            "key_type": key_type,
            "public_key": _encode_base64(raw_response["public_key"]),
            "private_key": _encode_base64(raw_response["private_key"]),
            "private_key_ref": None,
            "storage_mode": storage_mode,
            "private_key_exported": True,
            "status": "active",
        }
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_operation(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="keygen",
            algorithm=raw_response["algorithm"],
            response_status=200,
            success=True,
            response_time_ms=elapsed_ms,
            audit_action="KEY_GENERATED",
            audit_status="success",
            resource_type="key",
            resource_id=str(key.id),
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "algorithm": raw_response["algorithm"],
                "operation": "keygen",
                "key_type": key_type,
                "key_id": str(key.id),
                "storage_mode": storage_mode,
                "endpoint": endpoint,
                "status": "success",
                "api_key_id": str(api_key_context.id),
            },
        )
        return response
    except HTTPException as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_failure(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="keygen",
            algorithm=algorithm,
            response_status=exc.status_code,
            response_time_ms=elapsed_ms,
            audit_action="KEY_GENERATION_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="key",
            error_type=exc.detail if isinstance(exc.detail, str) else "HTTP_ERROR",
            details={
                "algorithm": algorithm,
                "operation": "keygen",
                "storage_mode": storage_mode,
                "endpoint": endpoint,
                "status": "failed",
                "api_key_id": str(api_key_context.id),
            },
        )
        raise
    except SQLAlchemyError as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_failure(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="keygen",
            algorithm=algorithm,
            response_status=500,
            response_time_ms=elapsed_ms,
            audit_action="KEY_GENERATION_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="key",
            error_type="DATABASE_ERROR",
            details={
                "algorithm": algorithm,
                "operation": "keygen",
                "storage_mode": storage_mode,
                "endpoint": endpoint,
                "status": "failed",
                "api_key_id": str(api_key_context.id),
            },
        )
        raise HTTPException(status_code=500, detail="Failed to store key metadata") from exc


def run_kem_encapsulation(
    *,
    api_key_context: ApiKeyContext,
    algorithm: str,
    public_key: str,
    endpoint: str,
    method: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    start = time.perf_counter()
    try:
        decoded_public_key = _decode_base64(public_key, "public_key")
        result = kem_service.encapsulate_secret(algorithm, decoded_public_key)
        response = {
            "algorithm": result["algorithm"],
            "ciphertext": _encode_base64(result["ciphertext"]),
            "shared_secret": _encode_base64(result["shared_secret"]),
            "status": "success",
        }
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_operation(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="kem_encapsulate",
            algorithm=result["algorithm"],
            response_status=200,
            success=True,
            response_time_ms=elapsed_ms,
            audit_action="KEM_ENCAPSULATED",
            audit_status="success",
            resource_type="kem_operation",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "algorithm": result["algorithm"],
                "operation": "kem_encapsulate",
                "key_type": "kem",
                "endpoint": endpoint,
                "status": "success",
                "api_key_id": str(api_key_context.id),
            },
        )
        return response
    except HTTPException as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_failure(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="kem_encapsulate",
            algorithm=algorithm,
            response_status=exc.status_code,
            response_time_ms=elapsed_ms,
            audit_action="KEM_ENCAPSULATION_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="kem_operation",
            error_type=exc.detail if isinstance(exc.detail, str) else "HTTP_ERROR",
            details={
                "algorithm": algorithm,
                "operation": "kem_encapsulate",
                "key_type": "kem",
                "endpoint": endpoint,
                "status": "failed",
                "api_key_id": str(api_key_context.id),
            },
        )
        raise


def run_kem_decapsulation(
    *,
    api_key_context: ApiKeyContext,
    algorithm: str,
    ciphertext: str,
    private_key: str,
    endpoint: str,
    method: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    start = time.perf_counter()
    try:
        decoded_ciphertext = _decode_base64(ciphertext, "ciphertext")
        decoded_private_key = _decode_base64(private_key, "private_key")
        result = kem_service.decapsulate_secret(algorithm, decoded_ciphertext, decoded_private_key)
        response = {
            "algorithm": result["algorithm"],
            "shared_secret": _encode_base64(result["shared_secret"]),
            "status": "success",
        }
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_operation(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="kem_decapsulate",
            algorithm=result["algorithm"],
            response_status=200,
            success=True,
            response_time_ms=elapsed_ms,
            audit_action="KEM_DECAPSULATED",
            audit_status="success",
            resource_type="kem_operation",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "algorithm": result["algorithm"],
                "operation": "kem_decapsulate",
                "key_type": "kem",
                "endpoint": endpoint,
                "status": "success",
                "api_key_id": str(api_key_context.id),
            },
        )
        return response
    except HTTPException as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_failure(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="kem_decapsulate",
            algorithm=algorithm,
            response_status=exc.status_code,
            response_time_ms=elapsed_ms,
            audit_action="KEM_DECAPSULATION_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="kem_operation",
            error_type=exc.detail if isinstance(exc.detail, str) else "HTTP_ERROR",
            details={
                "algorithm": algorithm,
                "operation": "kem_decapsulate",
                "key_type": "kem",
                "endpoint": endpoint,
                "status": "failed",
                "api_key_id": str(api_key_context.id),
            },
        )
        raise


def run_sign_operation(
    *,
    api_key_context: ApiKeyContext,
    algorithm: str,
    message: str,
    private_key: str,
    endpoint: str,
    method: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    start = time.perf_counter()
    try:
        decoded_private_key = _decode_base64(private_key, "private_key")
        result = dsa_service.sign_message(algorithm, message.encode("utf-8"), decoded_private_key)
        response = {
            "algorithm": result["algorithm"],
            "signature": _encode_base64(result["signature"]),
            "status": "success",
        }
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_operation(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="sign",
            algorithm=result["algorithm"],
            response_status=200,
            success=True,
            response_time_ms=elapsed_ms,
            audit_action="SIGNATURE_CREATED",
            audit_status="success",
            resource_type="signature_operation",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "algorithm": result["algorithm"],
                "operation": "sign",
                "key_type": "signature",
                "endpoint": endpoint,
                "status": "success",
                "api_key_id": str(api_key_context.id),
            },
        )
        return response
    except HTTPException as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_failure(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="sign",
            algorithm=algorithm,
            response_status=exc.status_code,
            response_time_ms=elapsed_ms,
            audit_action="SIGNATURE_CREATION_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="signature_operation",
            error_type=exc.detail if isinstance(exc.detail, str) else "HTTP_ERROR",
            details={
                "algorithm": algorithm,
                "operation": "sign",
                "key_type": "signature",
                "endpoint": endpoint,
                "status": "failed",
                "api_key_id": str(api_key_context.id),
            },
        )
        raise


def run_verify_operation(
    *,
    api_key_context: ApiKeyContext,
    algorithm: str,
    message: str,
    signature: str,
    public_key: str,
    endpoint: str,
    method: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    start = time.perf_counter()
    try:
        decoded_signature = _decode_base64(signature, "signature")
        decoded_public_key = _decode_base64(public_key, "public_key")
        result = dsa_service.verify_signature(
            algorithm,
            message.encode("utf-8"),
            decoded_signature,
            decoded_public_key,
        )
        is_valid = result["is_valid"]
        response = {
            "algorithm": result["algorithm"],
            "is_valid": is_valid,
            "status": "success",
        }
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_operation(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="verify",
            algorithm=result["algorithm"],
            response_status=200,
            success=True,
            response_time_ms=elapsed_ms,
            audit_action="SIGNATURE_VERIFIED" if is_valid else "SIGNATURE_VERIFICATION_FAILED",
            audit_status="success" if is_valid else "failed",
            resource_type="signature_operation",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "algorithm": result["algorithm"],
                "operation": "verify",
                "key_type": "signature",
                "endpoint": endpoint,
                "status": "success" if is_valid else "failed",
                "api_key_id": str(api_key_context.id),
            },
        )
        return response
    except HTTPException as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _record_failure(
            api_key_context=api_key_context,
            endpoint=endpoint,
            method=method,
            operation="verify",
            algorithm=algorithm,
            response_status=exc.status_code,
            response_time_ms=elapsed_ms,
            audit_action="SIGNATURE_VERIFICATION_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="signature_operation",
            error_type=exc.detail if isinstance(exc.detail, str) else "HTTP_ERROR",
            details={
                "algorithm": algorithm,
                "operation": "verify",
                "key_type": "signature",
                "endpoint": endpoint,
                "status": "failed",
                "api_key_id": str(api_key_context.id),
            },
        )
        raise