import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def make_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "status": status_code
            }
        }
    )


class AppError(Exception):
    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, status_code: int | None = None, error_code: str | None = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code


class ValidationError(AppError):
    status_code = 400
    error_code = "validation_error"


class AlgorithmNotSupportedError(AppError):
    status_code = 400
    error_code = "algorithm_not_supported"


class KeygenError(AppError):
    status_code = 500
    error_code = "keygen_failed"


class EncapsulationError(AppError):
    status_code = 400
    error_code = "encapsulation_failed"


class DecapsulationError(AppError):
    status_code = 400
    error_code = "decapsulation_failed"


class DatabaseError(AppError):
    status_code = 500
    error_code = "database_error"


# Handlers

async def app_error_handler(request: Request, exc: AppError):
    if exc.status_code >= 500:
        logger.exception("AppError caught: %s (code: %s, status: %d)", exc.message, exc.error_code, exc.status_code)
    else:
        logger.warning("AppError caught: %s (code: %s, status: %d)", exc.message, exc.error_code, exc.status_code)
    return make_error_response(exc.status_code, exc.error_code, exc.message)


async def http_exception_handler(request: Request, exc: HTTPException):
    status_code = exc.status_code
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    if status_code == 401:
        code = "unauthorized"
    elif status_code == 403:
        code = "forbidden"
    elif status_code == 404:
        code = "not_found"
    elif status_code == 400:
        if "replay" in message.lower():
            code = "replay_attack_detected"
        elif "signature" in message.lower():
            code = "invalid_signature"
        elif "timestamp" in message.lower():
            code = "invalid_timestamp"
        elif "algorithm" in message.lower() and ("unsupported" in message.lower() or "disabled" in message.lower() or "not supported" in message.lower()):
            code = "algorithm_not_supported"
        else:
            code = "bad_request"
    elif status_code == 422:
        code = "validation_error"
    else:
        code = "internal_error"

    logger.warning("HTTPException caught: %s (status: %d)", message, status_code)
    return make_error_response(status_code, code, message)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msgs = []
    for err in errors:
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Unknown error")
        error_msgs.append(f"{loc}: {msg}")

    message = "Validation failed: " + "; ".join(error_msgs)
    logger.warning("RequestValidationError caught: %s", message)
    return make_error_response(422, "validation_error", message)


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("SQLAlchemy Database Error occurred", exc_info=exc)
    return make_error_response(500, "database_error", "A database error occurred.")


async def catch_all_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception for %s %s", request.method, request.url.path, exc_info=exc)
    return make_error_response(500, "internal_error", "Internal Server Error")
