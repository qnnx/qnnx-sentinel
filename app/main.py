from fastapi import FastAPI
from app.core.config import settings
from app.routes.algorithms import router as algorithms_router
from app.routes.health import router as health_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(algorithms_router, prefix=settings.API_V1_STR, tags=["Algorithms"])
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])

@app.get("/", include_in_schema=False)
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for documentation."}
