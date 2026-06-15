from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.algorithm import Algorithm
from app.repositories._types import as_uuid

class AlgorithmRepository:

    def get_all(self, db: Session):
        return db.query(Algorithm).all()

    def get_by_id(self, db: Session, algorithm_id: str):
        return db.query(Algorithm).filter(Algorithm.id == as_uuid(algorithm_id)).first()

    def get_by_algo_id(self, db: Session, algo_id: str):
        return db.query(Algorithm).filter(Algorithm.algo_id == algo_id).first()

    def get_by_name(self, db: Session, name: str):
        return db.query(Algorithm).filter(func.lower(Algorithm.name) == name.lower()).first()

    def get_by_identifier(self, db: Session, identifier: str):
        normalized = identifier.lower()
        return (
            db.query(Algorithm)
            .filter(
                (func.lower(Algorithm.name) == normalized)
                | (func.lower(Algorithm.algo_id) == normalized)
            )
            .first()
        )

    def create(self, db: Session, algorithm_data: dict):
        algorithm = Algorithm(**algorithm_data)
        db.add(algorithm)
        db.commit()
        db.refresh(algorithm)
        return algorithm

    def update(self, db: Session, algorithm_id: str, update_data: dict):
        algorithm = self.get_by_id(db, algorithm_id)

        if not algorithm:
            return None

        for key, value in update_data.items():
            setattr(algorithm, key, value)

        db.commit()
        db.refresh(algorithm)
        return algorithm

    def delete(self, db: Session, algorithm_id: str):
        algorithm = self.get_by_id(db, algorithm_id)

        if not algorithm:
            return None

        db.delete(algorithm)
        db.commit()
        return algorithm