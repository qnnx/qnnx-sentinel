from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "QNNX-Sentinel"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Post-Quantum Cryptography API for QNNX-Sentinel"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    DISABLE_SIGNED_REQUEST_GUARDS: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
