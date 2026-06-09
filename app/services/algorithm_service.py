from typing import List
from app.schemas.algorithms import AlgorithmInfo, AlgorithmsResponse

ALGORITHMS: List[AlgorithmInfo] = [
    AlgorithmInfo(
        id="ml-kem-512",
        name="ML-KEM-512",
        type="KEM",
        security_level=1,
        standard="FIPS 203",
        description="Module Lattice Key Encapsulation Mechanism - 128-bit security"
    ),
    AlgorithmInfo(
        id="ml-kem-768",
        name="ML-KEM-768",
        type="KEM",
        security_level=3,
        standard="FIPS 203",
        description="Module Lattice Key Encapsulation Mechanism - 192-bit security"
    ),
    AlgorithmInfo(
        id="ml-kem-1024",
        name="ML-KEM-1024",
        type="KEM",
        security_level=5,
        standard="FIPS 203",
        description="Module Lattice Key Encapsulation Mechanism - 256-bit security"
    ),
    AlgorithmInfo(
        id="ml-dsa-44",
        name="ML-DSA-44",
        type="DSA",
        security_level=2,
        standard="FIPS 204",
        description="Module Lattice Digital Signature Algorithm - 128-bit security"
    ),
    AlgorithmInfo(
        id="ml-dsa-65",
        name="ML-DSA-65",
        type="DSA",
        security_level=3,
        standard="FIPS 204",
        description="Module Lattice Digital Signature Algorithm - 192-bit security"
    ),
    AlgorithmInfo(
        id="ml-dsa-87",
        name="ML-DSA-87",
        type="DSA",
        security_level=5,
        standard="FIPS 204",
        description="Module Lattice Digital Signature Algorithm - 256-bit security"
    ),
]

def get_all_algorithms() -> AlgorithmsResponse:
    return AlgorithmsResponse(
        total=len(ALGORITHMS),
        algorithms=ALGORITHMS
    )
