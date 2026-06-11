from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.database import SessionLocal
from app.repositories.api_nonce_repo import APINonceRepository
from app.schemas.api_nonce import ApiNonceResponse

api_nonce_repository = APINonceRepository()


def create_api_nonce(api_key_id: str, nonce: str) -> ApiNonceResponse:
    db = SessionLocal()
    try:
        api_nonce = api_nonce_repository.create(
            db,
            {
                "api_key_id": api_key_id,
                "nonce": nonce,
            },
        )
        return ApiNonceResponse.model_validate(api_nonce, from_attributes=True)
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Nonce already exists for this API key") from exc
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()
