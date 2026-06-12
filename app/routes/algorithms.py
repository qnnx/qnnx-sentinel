from fastapi import APIRouter
from app.schemas.algorithms import AlgorithmsResponse, AlgorithmInfo
from app.services.algorithm_service import get_all_algorithms, get_algorithm_by_name

router = APIRouter()

@router.get(
    "/algorithms",
    response_model=AlgorithmsResponse,
    summary="List PQC Algorithms",
    description="Returns all supported Post-Quantum Cryptography algorithms in the registry."
)
def list_algorithms():
    return get_all_algorithms()

@router.get(
    "/algorithms/{name}",
    response_model=AlgorithmInfo,
    summary="Get Algorithm by Name",
    description="Returns full details of a specific PQC algorithm by name. Example: ML-KEM-768"
)
def get_algorithm(name: str):
    return get_algorithm_by_name(name)