from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
import app.models
from app.core.config import settings
from app.core.exceptions import (
    bad_request_handler,
    unauthorized_handler,
    forbidden_handler,
    not_found_handler,
    validation_error_handler,
    internal_server_error_handler
)
from app.routes.algorithms import router as algorithms_router
from app.routes.health import router as health_router
from app.routes.kem import router as kem_router
from app.routes.dsa import router as dsa_router
from app.routes.audit_logs import router as audit_logs_router
from app.routes.api_usage import router as usage_router
from app.routes.keygen import router as keygen_router
from app.core.limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from app.gateway.socket_server import start_gateway_server
import logging
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch the raw-socket VPN gateway listener on the same
    # event loop as the FastAPI/SlowAPI HTTP server.
    gateway_server = await start_gateway_server()
    app.state.gateway_server = gateway_server

    yield  # app runs normally here until shutdown is triggered

    # Shutdown: close the gateway listener cleanly so no connections
    # are left dangling when the process stops.
    gateway_server.close()
    await gateway_server.wait_closed()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Store the limiter in the app state
app.state.limiter = limiter

# Add the SlowAPI middleware to intercept requests
app.add_middleware(SlowAPIMiddleware)

def rate_limit_custom_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "status_code": 429,
            "error": "Rate limit exceeded"
        }
    )

# Error Handlers
app.add_exception_handler(400, bad_request_handler)
app.add_exception_handler(401, unauthorized_handler)
app.add_exception_handler(403, forbidden_handler)
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(500, internal_server_error_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_custom_handler)

# Routes
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(algorithms_router, prefix=settings.API_V1_STR, tags=["Algorithms"])
app.include_router(keygen_router, prefix=settings.API_V1_STR, tags=["Key Generation"])
app.include_router(kem_router, prefix=settings.API_V1_STR, tags=["KEM"])
app.include_router(dsa_router, prefix=settings.API_V1_STR, tags=["DSA"])
app.include_router(audit_logs_router, prefix=settings.API_V1_STR, tags=["Audit Logs"])
app.include_router(usage_router, prefix=settings.API_V1_STR, tags=["Usage"])

@app.get("/", include_in_schema=False)
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for documentation."}