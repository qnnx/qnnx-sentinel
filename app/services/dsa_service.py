from app.crypto.dsa import DSAManager


SUPPORTED_DSAS = {name.casefold(): name for name in DSAManager.get_supported_dsas()}


def _resolve_algorithm(algorithm: str) -> str:
    normalized_algorithm = algorithm.strip().casefold()
    return SUPPORTED_DSAS.get(normalized_algorithm, algorithm.strip())


def generate_dsa_keypair(algorithm: str) -> dict:
    algorithm = _resolve_algorithm(algorithm)
    keys = DSAManager.generate_keypair(algorithm)
    return {
        "algorithm": algorithm,
        "public_key": keys["public_key"],
        "private_key": keys["private_key"],
    }


def sign_message(algorithm: str, message: bytes, private_key: bytes) -> dict:
    algorithm = _resolve_algorithm(algorithm)
    signature_data = DSAManager.sign(algorithm, message, private_key)
    return {
        "algorithm": algorithm,
        "signature": signature_data["signature"],
    }


def verify_signature(algorithm: str, message: bytes, signature: bytes, public_key: bytes) -> dict:
    algorithm = _resolve_algorithm(algorithm)
    verification_data = DSAManager.verify(algorithm, message, signature, public_key)
    return {
        "algorithm": algorithm,
        "is_valid": verification_data["is_valid"],
    }
