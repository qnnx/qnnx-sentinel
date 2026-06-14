from fastapi import HTTPException

from app.core.database import SessionLocal
from app.models.algorithm import Algorithm
from app.repositories.algorithm_repo import AlgorithmRepository
from app.schemas.algorithms import AlgorithmInfo, AlgorithmsResponse
from app.services.algorithm_support import is_algorithm_executable

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
        algo_type=algorithm.algo_type,
        family=algorithm.family,
        public_key_size=algorithm.public_key_size,
        private_key_size=algorithm.private_key_size,
        ciphertext_size=algorithm.ciphertext_size,
    )


def get_all_algorithms() -> AlgorithmsResponse:
    db = SessionLocal()
    try:
        algorithms = [
            algorithm
            for algorithm in algorithm_repository.get_all(db)
            if (algorithm.status or "").lower() in {"active", "enabled", "recommended"}
            and is_algorithm_executable(algorithm.name, algorithm.type)
        ]
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
        if not algorithm or not is_algorithm_executable(algorithm.name, algorithm.type):
            raise HTTPException(status_code=404, detail="Algorithm not found")
        return _to_algorithm_info(algorithm)
    finally:
        db.close()
