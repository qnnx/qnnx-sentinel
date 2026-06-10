import sys
import os

# --- PATHING FIX ---
# This ensures Python can find the 'schemas' and 'services' folders 
# even if you click the Play button from inside this file.
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
# -------------------

import uuid

# Import our underlying services EXACTLY as you named them
from services import kem_services, dsa_services

# Import the schemas needed to communicate with those services
from schemas.kem import KeyGenRequest as KEMRequest
from schemas.dsa import KeyGenRequest as DSARequest

# Define our recognized algorithms for routing
SUPPORTED_KEMS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024", "Kyber512", "Kyber768", "Kyber1024"]
SUPPORTED_DSAS = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87", "Dilithium2", "Dilithium3", "Dilithium5"]

def generate_keypair(algorithm: str) -> dict:
    """
    Master function to generate keys. Routes to KEM or DSA based on the algorithm,
    and returns a standardized API response ready for database tracking.
    """
    
    # 1. Identify the algorithm type and route to the correct service
    if algorithm in SUPPORTED_KEMS:
        key_type = "kem"
        request_schema = KEMRequest(algorithm=algorithm)
        # Calling kem_services with the 's'
        raw_response = kem_services.generate_kem_keypair(request_schema)
        
    elif algorithm in SUPPORTED_DSAS:
        key_type = "dsa"
        request_schema = DSARequest(algorithm=algorithm)
        # Calling dsa_services with the 's'
        raw_response = dsa_services.generate_dsa_keypair(request_schema)
        
    else:
        return {
            "success": False,
            "error": f"Unsupported algorithm: '{algorithm}'. Must be a valid KEM or DSA."
        }

    # 2. Generate a Mock ID for database storage later
    new_key_id = str(uuid.uuid4())
    final_public_key = raw_response.public_key

    # 3. Construct the standardized response payload
    return {
        "success": True,
        "key": {
            "key_id": new_key_id,
            "algorithm": algorithm,
            "key_type": key_type,
            "public_key": final_public_key,
            "status": "created"
        },
        "private_key_export": raw_response.private_key 
    }

