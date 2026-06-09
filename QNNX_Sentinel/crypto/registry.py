ALGORITHM_REGISTRY = {
    "ml-kem-768": {
        "type": "KEM",
        "security_level": 3,
        "nist_standard": "FIPS 203"
    },
    "ml-dsa-65": {
        "type": "SIG",
        "security_level": 3,
        "nist_standard": "FIPS 204"
    }
}

def get_algorithm_info(algo_name):
    return ALGORITHM_REGISTRY.get(algo_name, "Algorithm not found")