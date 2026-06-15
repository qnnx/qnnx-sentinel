# ==========================================
# 1. INDIVIDUAL METADATA DEFINITIONS
# ==========================================
# (Variables use underscores so they are valid Python names)

ML_KEM_512_META = {
    "type": "KEM",
    "security_level": 1,
    "nist_standard": "FIPS 203",
    "public_key_size": "800 bytes"
}

ML_KEM_768_META = {
    "type": "KEM",
    "security_level": 3,
    "nist_standard": "FIPS 203",
    "public_key_size": "1184 bytes"
}

ML_KEM_1024_META = {
    "type": "KEM",
    "security_level": 5,
    "nist_standard": "FIPS 203",
    "public_key_size": "1586 bytes"
}

ML_DSA_44_META = {
    "type": "SIG",
    "security_level": 2,
    "nist_standard": "FIPS 204",
    "public_key_size": "1312 bytes"
}

ML_DSA_65_META = {
    "type": "SIG",
    "security_level": 3,
    "nist_standard": "FIPS 204",
    "public_key_size": "1952 bytes"
}

ML_DSA_87_META = {
    "type": "SIG",
    "security_level": 5,
    "nist_standard": "FIPS 204",
    "public_key_size": "2592 bytes"
}


# ==========================================
# 2. CENTRAL ALGORITHM REGISTRY MAPPING
# ==========================================
# (Maps all variant string names to the corresponding definitions)

ALGORITHM_REGISTRY = {
    # ML-KEM-512 Aliases
    "ml-kem-512": ML_KEM_512_META,
    "kyber-512": ML_KEM_512_META,
    "ml-kem-512/kyber-512": ML_KEM_512_META,
    
    # ML-KEM-768 Aliases
    "ml-kem-768": ML_KEM_768_META,
    "kyber-768": ML_KEM_768_META,
    "ml-kem-768/kyber-768": ML_KEM_768_META,
    
    # ML-KEM-1024 Aliases
    "ml-kem-1024": ML_KEM_1024_META,
    "kyber-1024": ML_KEM_1024_META,
    "ml-kem-1024/kyber-1024": ML_KEM_1024_META,
    
    # ML-DSA-44 Aliases
    "ml-dsa-44": ML_DSA_44_META,
    "dilithium-44": ML_DSA_44_META,
    "ml-dsa-44/dilithium-44": ML_DSA_44_META,
    
    # ML-DSA-65 Aliases
    "ml-dsa-65": ML_DSA_65_META,
    "dilithium-65": ML_DSA_65_META,
    "ml-dsa-65/dilithium-65": ML_DSA_65_META,
    
    # ML-DSA-87 Aliases
    "ml-dsa-87": ML_DSA_87_META,
    "dilithium-87": ML_DSA_87_META,
    "ml-dsa-87/dilithium-87": ML_DSA_87_META
}


# ==========================================
# 3. LOOKUP INTERFACE FUNCTION
# ==========================================

def get_algorithm_info(algo_name=None):
    """
    Retrieves info for a specific algorithm name or alias.
    If no name is passed, returns the complete registry dictionary.
    """
    if algo_name is None:
        return ALGORITHM_REGISTRY
        
    # Standardize input to lowercase and strip whitespace to prevent accidental typos
    normalized_name = algo_name.lower().strip()
    
    return ALGORITHM_REGISTRY.get(normalized_name, {"error": f"Algorithm '{algo_name}' not found"})