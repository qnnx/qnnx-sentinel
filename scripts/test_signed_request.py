import argparse
import urllib.error
import urllib.request
from datetime import datetime, timezone
from uuid import uuid4

from app.security.request_signature import create_request_signature


def build_headers(api_key: str, method: str, path: str, body: bytes) -> dict[str, str]:
    timestamp = datetime.now(timezone.utc).isoformat()
    nonce = uuid4().hex
    signature = create_request_signature(
        method=method,
        path=path,
        timestamp=timestamp,
        nonce=nonce,
        body=body,
        secret=api_key,
    )
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-QNNX-Timestamp": timestamp,
        "X-QNNX-Nonce": nonce,
        "X-QNNX-Signature": signature,
    }


def main():
    parser = argparse.ArgumentParser(description="Send a signed request to the QNNX PQC API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--path", required=True, help="Example: /api/v1/keygen")
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--method", default="POST")
    parser.add_argument("--body", default='{"algorithm":"ML-KEM-768"}')
    args = parser.parse_args()

    body = args.body.encode("utf-8")
    headers = build_headers(args.api_key, args.method.upper(), args.path, body)
    request = urllib.request.Request(
        url=f"{args.base_url.rstrip('/')}{args.path}",
        data=body,
        headers=headers,
        method=args.method.upper(),
    )

    try:
        with urllib.request.urlopen(request) as response:
            print(f"Status: {response.status}")
            print(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(f"Status: {exc.code}")
        print(exc.read().decode("utf-8"))


if __name__ == "__main__":
    main()
