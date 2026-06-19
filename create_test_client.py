"""
One-off script to create a single test client row, for manually testing
the gateway's socket handshake end-to-end. Not part of the actual ticket --
delete this file once a real /clients registration route exists.
"""
import uuid

from app.core.database import SessionLocal
from app.services.kem_service import generate_kem_keypair
from app.repositories.client_repo import ClientRepository

client_repo = ClientRepository()

ALGORITHM = "ML-KEM-768"
CLIENT_IDENTIFIER = "test-client-1"

def main():
    db = SessionLocal()
    try:
        keys = generate_kem_keypair(ALGORITHM)

        client = client_repo.create(db, {
            "id": uuid.uuid4(),
            "client_identifier": CLIENT_IDENTIFIER,
            "kem_algorithm": ALGORITHM,
            "public_key": keys["public_key"],
            "private_key": keys["private_key"],
        })

        print(f"Created client: {client.client_identifier} (id={client.id})")
        print(f"Public key length: {len(keys['public_key'])} bytes")

    finally:
        db.close()

if __name__ == "__main__":
    main()