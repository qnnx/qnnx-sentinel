import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)

def error_response(success: bool, status_code: int, error: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": success,
            "status_code": status_code,
            "error": error
        }
    )

async def bad_request_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException) and isinstance(exc.detail, str):
        return error_response(False, 400, exc.detail)
    return error_response(False, 400, "Bad Request")

async def unauthorized_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException) and isinstance(exc.detail, str):
        return error_response(False, 401, exc.detail)
    return error_response(False, 401, "Unauthorized")

async def forbidden_handler(request: Request, exc: Exception):
    return error_response(False, 403, "Forbidden")

async def not_found_handler(request: Request, exc: Exception):
    return error_response(False, 404, "Not Found")

async def validation_error_handler(request: Request, exc: RequestValidationError):
    return error_response(False, 422, "Validation Error")

async def internal_server_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error for %s %s", request.method, request.url.path, exc_info=exc)
    return error_response(False, 500, "Internal Server Error")
