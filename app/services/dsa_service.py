from crypto.dsa import DSAManager
from schemas.dsa import (
    KeyGenRequest, KeyGenResponse,
    SignRequest, SignResponse,
    VerifyRequest, VerifyResponse
)

def generate_dsa_keypair(request: KeyGenRequest) -> KeyGenResponse:
    keys = DSAManager.generate_keypair(request.algorithm)
    
    return KeyGenResponse(
        public_key=keys["public_key"].hex(),
        private_key=keys["private_key"].hex()
    )

def sign_message(request: SignRequest) -> SignResponse:
    # 1. Convert hex key to bytes, and string message to bytes
    priv_key_bytes = bytes.fromhex(request.private_key)
    message_bytes = request.message.encode('utf-8')
    
    # 2. Call the crypto module
    sig_data = DSAManager.sign(request.algorithm, message_bytes, priv_key_bytes)
    
    # 3. Extract the raw bytes from the dictionary and convert to hex string
    return SignResponse(
        signature=sig_data["signature"].hex()
    )

def verify_signature(request: VerifyRequest) -> VerifyResponse:
    # 1. Convert everything back to bytes
    message_bytes = request.message.encode('utf-8')
    sig_bytes = bytes.fromhex(request.signature)
    pub_key_bytes = bytes.fromhex(request.public_key)
    
    # 2. Call the engine (returns a dictionary)
    verification_data = DSAManager.verify(request.algorithm, message_bytes, sig_bytes, pub_key_bytes)
    
    # 3. Extract the boolean from the dictionary
    return VerifyResponse(
        is_valid=verification_data["is_valid"]
    )