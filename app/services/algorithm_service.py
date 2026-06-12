from fastapi import HTTPException

from app.core.database import SessionLocal
from app.models.algorithm import Algorithm
from app.repositories.algorithm_repo import AlgorithmRepository
from app.schemas.algorithms import AlgorithmInfo, AlgorithmsResponse

algorithm_repository = AlgorithmRepository()


def _to_algorithm_info(algorithm: Algorithm) -> AlgorithmInfo:
    return AlgorithmInfo(
        algo_id=algorithm.algo_id,
        name=algorithm.name,
        type=algorithm.type,
        security_level=algorithm.security_level,
        standard=algorithm.nist_standard,
        description=algorithm.description,
        status=algorithm.status,
        recommended_use=algorithm.recommended_use,
    )


def get_all_algorithms() -> AlgorithmsResponse:
    db = SessionLocal()
    try:
        algorithms = algorithm_repository.get_all(db)
        algorithm_items = [_to_algorithm_info(algorithm) for algorithm in algorithms]
        return AlgorithmsResponse(
            total=len(algorithm_items),
            algorithms=algorithm_items,
        )
    finally:
        db.close()


def get_algorithm_by_name(name: str) -> AlgorithmInfo:
    db = SessionLocal()
    try:
        algorithm = algorithm_repository.get_by_name(db, name)
        if not algorithm:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        return _to_algorithm_info(algorithm)
    finally:
        db.close()