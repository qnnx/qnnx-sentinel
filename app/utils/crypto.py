import hashlib
import hmac
import secrets


def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hmac_sha256_hex(secret: str, message: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def constant_time_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)
