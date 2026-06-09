from fastapi import APIRouter
from app.schemas.algorithms import AlgorithmsResponse
from app.services.algorithm_service import get_all_algorithms

router = APIRouter()

@router.get(
    "/algorithms",
    response_model=AlgorithmsResponse,
    summary="List PQC Algorithms",
    description="Returns all supported Post-Quantum Cryptography algorithms in the registry."
)
def list_algorithms():
    return get_all_algorithms()
