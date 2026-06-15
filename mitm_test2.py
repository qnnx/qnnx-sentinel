import base64
import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timezone

import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

BASE_URL = "http://127.0.0.1:8000/api/v1"

KEM_ALG = "ML-KEM-768"
DSA_ALG = "ML-DSA-65"

API_KEY = os.getenv("QNNX_API_KEY")
SIGNING_SECRET = os.getenv("QNNX_SIGNING_SECRET")


def create_request_signature(method, path, timestamp, nonce, body, secret):
    payload = (
        method.upper().encode("utf-8")
        + path.encode("utf-8")
        + timestamp.encode("utf-8")
        + nonce.encode("utf-8")
        + body
    )
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

def build_request(path, body):
    timestamp = datetime.now(timezone.utc).isoformat()
    nonce = str(uuid.uuid4())
    body_bytes = json.dumps(body, separators=(",", ":")).encode("utf-8")
    signature = create_request_signature(
        method="POST",
        path=f"/api/v1{path}",
        timestamp=timestamp,
        nonce=nonce,
        body=body_bytes,
        secret=SIGNING_SECRET,
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-QNNX-Signing-Secret": SIGNING_SECRET,
        "X-QNNX-Timestamp": timestamp,
        "X-QNNX-Nonce": nonce,
        "X-QNNX-Signature": signature,
    }
    return body_bytes, headers




def post(path, body):
    body_bytes, headers = build_request(path, body)
    res = requests.post(f"{BASE_URL}{path}", data=body_bytes, headers=headers, timeout=30)
    print(path, res.status_code)

    if res.status_code >= 400:
        print(res.text)
        raise Exception("API request failed")

    return res.json()


def derive_aes_key(shared_secret_hex):
    shared_secret = base64.b64decode(shared_secret_hex)
    return hashlib.sha256(shared_secret).digest()


def encrypt_message(message, key):
    aesgcm = AESGCM(key)
    nonce = b"123456789012"
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
    return base64.b64encode(nonce).decode("ascii"), base64.b64encode(ciphertext).decode("ascii")


def decrypt_message(nonce_hex, ciphertext_hex, key):
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(
        base64.b64decode(nonce_hex),
        base64.b64decode(ciphertext_hex),
        None
    )
    return plaintext.decode()


def tamper_encoded(encoded_data):
    data = bytearray(base64.b64decode(encoded_data))
    data[0] ^= 1
    return base64.b64encode(bytes(data)).decode("ascii")


def main():
    if not API_KEY or not SIGNING_SECRET:
        raise RuntimeError("Set QNNX_API_KEY and QNNX_SIGNING_SECRET before running this script")

    print("=== QNNX API Message MITM Test ===")

    # 1. Receiver creates KEM keypair
    kem_keypair = post("/keygen", {
        "algorithm": KEM_ALG
    })

    receiver_public_key = kem_keypair["public_key"]
    receiver_private_key = kem_keypair["private_key"]

    print("[PASS] Receiver KEM keypair generated")

    # 2. Sender encapsulates shared secret
    encap = post("/kem/encapsulate", {
        "algorithm": KEM_ALG,
        "public_key": receiver_public_key
    })

    kem_ciphertext = encap["ciphertext"]
    sender_shared_secret = encap["shared_secret"]

    print("[PASS] Sender created KEM shared secret")

    # 3. Receiver decapsulates shared secret
    decap = post("/kem/decapsulate", {
        "algorithm": KEM_ALG,
        "ciphertext": kem_ciphertext,
        "private_key": receiver_private_key
    })

    receiver_shared_secret = decap["shared_secret"]

    assert sender_shared_secret == receiver_shared_secret
    print("[PASS] Receiver got same shared secret")

    # 4. Encrypt message locally using AES-GCM
    aes_key = derive_aes_key(sender_shared_secret)

    message = "Hello Receiver, this is a secure PQC message."
    nonce, encrypted_message = encrypt_message(message, aes_key)

    print("[PASS] Message encrypted locally using AES-GCM")

    # 5. Sender creates DSA keypair
    dsa_keypair = post("/keygen", {
        "algorithm": DSA_ALG
    })

    sender_public_sign_key = dsa_keypair["public_key"]
    sender_private_sign_key = dsa_keypair["private_key"]

    print("[PASS] Sender DSA keypair generated")

    # 6. Sender signs encrypted message using API
    sign = post("/sign", {
        "algorithm": DSA_ALG,
        "message": encrypted_message,
        "private_key": sender_private_sign_key
    })

    signature = sign["signature"]

    print("[PASS] Encrypted message signed")

    # 7. Receiver verifies normal message
    verify_normal = post("/verify", {
        "algorithm": DSA_ALG,
        "message": encrypted_message,
        "signature": signature,
        "public_key": sender_public_sign_key
    })

    if verify_normal["is_valid"] is True:
        decrypted = decrypt_message(nonce, encrypted_message, aes_key)
        print("[PASS] Normal message verified and decrypted")
        print("Message:", decrypted)
    else:
        print("[FAIL] Normal message rejected")

    print("-" * 50)

    # 8. MITM changes encrypted message
    tampered_message = tamper_encoded(encrypted_message)

    verify_tampered_msg = post("/verify", {
        "algorithm": DSA_ALG,
        "message": tampered_message,
        "signature": signature,
        "public_key": sender_public_sign_key
    })

    if verify_tampered_msg["is_valid"] is False:
        print("[PASS] MITM tampered ciphertext rejected")
    else:
        print("[FAIL] MITM tampered ciphertext accepted")

    print("-" * 50)

    # 9. MITM changes signature
    tampered_signature = tamper_encoded(signature)

    verify_tampered_sig = post("/verify", {
        "algorithm": DSA_ALG,
        "message": encrypted_message,
        "signature": tampered_signature,
        "public_key": sender_public_sign_key
    })

    if verify_tampered_sig["is_valid"] is False:
        print("[PASS] MITM tampered signature rejected")
    else:
        print("[FAIL] MITM tampered signature accepted")

    print("-" * 50)

    # 10. MITM changes sender public key
    fake_keypair = post("/keygen", {
        "algorithm": DSA_ALG
    })

    fake_public_key = fake_keypair["public_key"]

    verify_fake_key = post("/verify", {
        "algorithm": DSA_ALG,
        "message": encrypted_message,
        "signature": signature,
        "public_key": fake_public_key
    })

    if verify_fake_key["is_valid"] is False:
        print("[PASS] Fake sender public key rejected")
    else:
        print("[FAIL] Fake sender public key accepted")


if __name__ == "__main__":
    main()