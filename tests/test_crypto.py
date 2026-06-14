from app.services import dsa_service, kem_service


def test_ml_kem_encapsulation_decapsulation_match():
    keys = kem_service.generate_kem_keypair("ML-KEM-768")
    encapsulated = kem_service.encapsulate_secret("ML-KEM-768", keys["public_key"])
    decapsulated = kem_service.decapsulate_secret(
        "ML-KEM-768",
        encapsulated["ciphertext"],
        keys["private_key"],
    )
    assert encapsulated["shared_secret"] == decapsulated["shared_secret"]


def test_ml_dsa_sign_verify_and_tamper_rejection():
    keys = dsa_service.generate_dsa_keypair("ML-DSA-65")
    signature = dsa_service.sign_message(
        "ML-DSA-65",
        b"test payload",
        keys["private_key"],
    )
    assert dsa_service.verify_signature(
        "ML-DSA-65",
        b"test payload",
        signature["signature"],
        keys["public_key"],
    )["is_valid"]
    assert not dsa_service.verify_signature(
        "ML-DSA-65",
        b"tampered payload",
        signature["signature"],
        keys["public_key"],
    )["is_valid"]
