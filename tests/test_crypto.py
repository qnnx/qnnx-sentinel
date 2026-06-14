import pytest
from app.services import kem_service, dsa_service
from app.schemas.kem import KeyGenRequest as KEMRequest, EncapsulationRequest, DecapsulationRequest
from app.schemas.dsa import KeyGenRequest as DSARequest, SignRequest, VerifyRequest

def test_ml_kem_key_generation_success():
    """Verify ML-KEM-768 can successfully generate public/private key material."""
    request_schema = KEMRequest(algorithm="ML-KEM-768")
    response = kem_service.generate_kem_keypair(request_schema)
    
    assert response.public_key is not None
    assert response.private_key is not None
    assert isinstance(response.public_key, str)
    assert len(response.public_key) > 0

def test_ml_kem_encapsulation_decapsulation_match():
    """Verify that encapsulated ciphertexts yield matching shared secrets upon decapsulation."""
    # 1. Generate keypair
    keygen_request = KEMRequest(algorithm="ML-KEM-768")
    keys = kem_service.generate_kem_keypair(keygen_request)
    
    # 2. Package into a real EncapsulationRequest schema object
    encap_req = EncapsulationRequest(public_key=keys.public_key, algorithm="ML-KEM-768")
    encap_response = kem_service.encapsulate_secret(encap_req)
    
    assert encap_response.ciphertext is not None
    assert encap_response.shared_secret is not None
    
    # 3. Package into a real DecapsulationRequest schema object
    decap_req = DecapsulationRequest(
        private_key=keys.private_key, 
        ciphertext=encap_response.ciphertext, 
        algorithm="ML-KEM-768"
    )
    decap_response = kem_service.decapsulate_secret(decap_req)
    
    # Assert that the shared secrets match
    actual_secret = getattr(decap_response, "shared_secret", decap_response)
    assert actual_secret == encap_response.shared_secret, "Cryptographic Shared Secrets Mismatch!"


def test_ml_dsa_sign_and_verify_success():
    """Verify ML-DSA-65 can cleanly sign a raw payload and successfully verify the signature."""
    keygen_request = DSARequest(algorithm="ML-DSA-65")
    keys = dsa_service.generate_dsa_keypair(keygen_request)
    
    message_text = "test_payload"
    sign_req = SignRequest(private_key=keys.private_key, message=message_text, algorithm="ML-DSA-65")
    sign_response = dsa_service.sign_message(sign_req)
    
    assert sign_response is not None
    actual_signature = sign_response.signature
    
    verify_req = VerifyRequest(
        public_key=keys.public_key, 
        message=message_text, 
        signature=actual_signature,
        algorithm="ML-DSA-65"
    )
    is_valid = dsa_service.verify_signature(verify_req)
    
    # FIX: Extract the literal boolean from the Pydantic VerifyResponse object!
    assert is_valid.is_valid is True


def test_ml_dsa_tampered_message_verification_failure():
    """Verify that any modification to signed payload data results in an absolute verification failure."""
    keygen_request = DSARequest(algorithm="ML-DSA-65")
    keys = dsa_service.generate_dsa_keypair(keygen_request)
    
    original_message = "test_payload"
    sign_req = SignRequest(private_key=keys.private_key, message=original_message, algorithm="ML-DSA-65")
    sign_response = dsa_service.sign_message(sign_req)
    
    actual_signature = sign_response.signature
    
    # Introduce adversarial tampering
    tampered_message = "tampered_payload"
    
    verify_req = VerifyRequest(
        public_key=keys.public_key, 
        message=tampered_message, 
        signature=actual_signature, 
        algorithm="ML-DSA-65"
    )
    is_valid = dsa_service.verify_signature(verify_req)
    

    assert is_valid.is_valid is False, "Security Breached: Tampered message accepted!"