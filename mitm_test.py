import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import requests

from app.security.request_signature import create_request_signature

API_URL = os.getenv("QNNX_API_URL", "http://127.0.0.1:8000/api/v1/keygen")
API_KEY = os.getenv("QNNX_API_KEY")
SECRET = os.getenv("QNNX_SIGNING_SECRET")


def sign_request(body_bytes, timestamp, nonce, method="POST", path="/api/v1/keygen"):
    return create_request_signature(
        method=method,
        path=path,
        timestamp=timestamp,
        nonce=nonce,
        body=body_bytes,
        secret=SECRET,
    )


def send_request(body, signature=None, timestamp=None, nonce=None):
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    nonce = nonce or str(uuid.uuid4())
    body_bytes = json.dumps(body, separators=(",", ":")).encode("utf-8")

    if signature is None:
        signature = sign_request(body_bytes, timestamp, nonce)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-QNNX-Signing-Secret": SECRET,
        "X-QNNX-Timestamp": timestamp,
        "X-QNNX-Nonce": nonce,
        "X-QNNX-Signature": signature,
        "Content-Type": "application/json",
    }

    res = requests.post(API_URL, data=body_bytes, headers=headers, timeout=30)
    print("Status:", res.status_code)
    print("Response:", res.text)
    print("-" * 40)

    return timestamp, nonce, signature


def main():
    if not API_KEY or not SECRET:
        raise RuntimeError("Set QNNX_API_KEY and QNNX_SIGNING_SECRET before running this script")

    valid_body = {
        "algorithm": "ML-KEM-768",
        "storage_mode": "customer_managed",
    }

    print("1. Valid request")
    timestamp, nonce, signature = send_request(valid_body)

    print("2. Body tampering test")
    tampered_body = {
        "algorithm": "Kyber512",
        "storage_mode": "customer_managed",
    }
    send_request(tampered_body, signature=signature, timestamp=timestamp, nonce=str(uuid.uuid4()))

    print("3. Replay attack test")
    send_request(valid_body, signature=signature, timestamp=timestamp, nonce=nonce)

    print("4. Old timestamp test")
    old_timestamp = (datetime.now(timezone.utc) - timedelta(seconds=1000)).isoformat()
    send_request(valid_body, timestamp=old_timestamp)

    print("5. Invalid signature test")
    send_request(valid_body, signature="wrong_signature")


if __name__ == "__main__":
    main()