import base64
import binascii
import hashlib
import hmac

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hmac_sha256_hex(secret: str, message: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def constant_time_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)


def _decode_key_material(master_key: str) -> bytes:
    raw_key = master_key.strip()
    if not raw_key:
        raise ValueError("MASTER_KEY is empty")

    for decoder in (
        lambda value: base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)),
        bytes.fromhex,
    ):
        try:
            decoded = decoder(raw_key)
        except (binascii.Error, ValueError):
            continue
        if len(decoded) in {16, 24, 32}:
            return decoded

    return hashlib.sha256(raw_key.encode("utf-8")).digest()


def _decode_encrypted_secret(encrypted_value: str) -> tuple[bytes, bytes]:
    value = encrypted_value.strip()
    if not value:
        raise ValueError("Encrypted signing secret is empty")

    if value.startswith("v1:"):
        value = value[3:]

    if ":" in value:
        nonce_value, ciphertext_value = value.split(":", 1)
        try:
            nonce = base64.urlsafe_b64decode(nonce_value + "=" * (-len(nonce_value) % 4))
            ciphertext = base64.urlsafe_b64decode(
                ciphertext_value + "=" * (-len(ciphertext_value) % 4)
            )
        except binascii.Error:
            nonce = bytes.fromhex(nonce_value)
            ciphertext = bytes.fromhex(ciphertext_value)
        return nonce, ciphertext

    try:
        encrypted_bytes = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except binascii.Error as exc:
        raise ValueError("Encrypted signing secret is not valid base64") from exc
    if len(encrypted_bytes) <= 12:
        raise ValueError("Encrypted signing secret payload is too short")
    return encrypted_bytes[:12], encrypted_bytes[12:]


def decrypt_aes_gcm_secret(encrypted_value: str, master_key: str) -> str:
    key = _decode_key_material(master_key)
    nonce, ciphertext = _decode_encrypted_secret(encrypted_value)
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
