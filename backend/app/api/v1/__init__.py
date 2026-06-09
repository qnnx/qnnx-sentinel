from fastapi import APIRouter
from app.api.v1.routes import health, algorithms

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(algorithms.router, tags=["Algorithms"])