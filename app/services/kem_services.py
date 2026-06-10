from crypto.kem import KEMManager
from schemas.kem import (
    KeyGenRequest, KeyGenResponse,
    EncapsulationRequest, EncapsulationResponse,
    DecapsulationRequest, DecapsulationResponse
)

def generate_kem_keypair(request: KeyGenRequest) -> KeyGenResponse:
    # Get raw bytes from engine
    keys = KEMManager.generate_keypair(request.algorithm)
    
    # Return as hex strings
    return KeyGenResponse(
        public_key=keys["public_key"].hex(),
        private_key=keys["private_key"].hex()
    )

def encapsulate_secret(request: EncapsulationRequest) -> EncapsulationResponse:
    # Convert incoming hex string to raw bytes
    pub_key_bytes = bytes.fromhex(request.public_key)
    
    # Get raw bytes from engine
    encap = KEMManager.encapsulate(request.algorithm, pub_key_bytes)
    
    # Return as hex strings
    return EncapsulationResponse(
        ciphertext=encap["ciphertext"].hex(),
        shared_secret=encap["shared_secret"].hex()
    )

def decapsulate_secret(request: DecapsulationRequest) -> DecapsulationResponse:
    # Convert incoming hex strings to raw bytes
    cipher_bytes = bytes.fromhex(request.ciphertext)
    priv_key_bytes = bytes.fromhex(request.private_key)
    
    # Get raw bytes from engine
    decap = KEMManager.decapsulate(request.algorithm, cipher_bytes, priv_key_bytes)
    
    # Return as hex strings
    return DecapsulationResponse(
        shared_secret=decap["shared_secret"].hex()
    )