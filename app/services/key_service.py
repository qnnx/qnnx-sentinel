import base64
import uuid

from fastapi import HTTPException

from app.crypto.dsa import DSAManager
from app.crypto.kem import KEMManager
from app.services import dsa_service, kem_service


SUPPORTED_KEMS = {name.casefold(): name for name in KEMManager.get_supported_kems()}
SUPPORTED_DSAS = {name.casefold(): name for name in DSAManager.get_supported_dsas()}


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _resolve_algorithm(algorithm: str) -> tuple[str, str]:
    normalized_algorithm = algorithm.strip().casefold()
    if normalized_algorithm in SUPPORTED_KEMS:
        return "kem", SUPPORTED_KEMS[normalized_algorithm]
    if normalized_algorithm in SUPPORTED_DSAS:
        return "dsa", SUPPORTED_DSAS[normalized_algorithm]
    raise HTTPException(
        status_code=400,
        detail=f"Unsupported algorithm: '{algorithm}'",
    )


def generate_keypair(algorithm: str) -> dict:
    if not algorithm or not algorithm.strip():
        raise HTTPException(status_code=400, detail="algorithm is required")

    key_type, canonical_algorithm = _resolve_algorithm(algorithm)
    if key_type == "kem":
        raw_response = kem_service.generate_kem_keypair(canonical_algorithm)
    else:
        raw_response = dsa_service.generate_dsa_keypair(canonical_algorithm)

    return {
        "key_id": str(uuid.uuid4()),
        "algorithm": raw_response["algorithm"],
        "key_type": key_type,
        "public_key": _b64encode(raw_response["public_key"]),
        "private_key": _b64encode(raw_response["private_key"]),
        "status": "created",
    }
