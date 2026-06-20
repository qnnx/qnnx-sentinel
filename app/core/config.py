import os
import sys
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "QNNX-Sentinel"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Post-Quantum Cryptography API for QNNX-Sentinel"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    MASTER_KEY: str | None = None
    DISABLE_SIGNED_REQUEST_GUARDS: bool = False
    OQS_INSTALL_PATH: str | None = None
    KEYGEN_RATE_LIMIT: str = "30/minute"
    KEM_RATE_LIMIT: str = "100/minute"
    SIGN_RATE_LIMIT: str = "60/minute"
    VERIFY_RATE_LIMIT: str = "120/minute"

    @model_validator(mode="after")
    def validate_security_and_oqs(self) -> "Settings":
        # 1. Enforce MASTER_KEY if request signing guards are active
        if not self.DISABLE_SIGNED_REQUEST_GUARDS and not self.MASTER_KEY:
            raise ValueError("MASTER_KEY must be configured when DISABLE_SIGNED_REQUEST_GUARDS is False")

        # 2. Inject OQS_INSTALL_PATH to environment if set
        if self.OQS_INSTALL_PATH:
            os.environ["OQS_INSTALL_PATH"] = self.OQS_INSTALL_PATH

        # 3. Verify liboqs loadable
        try:
            # Import locally to avoid circular dependencies
            from app.crypto._oqs_loader import _configure_oqs_install_path, _require_liboqs
            _configure_oqs_install_path()
            _require_liboqs()
            import oqs
            oqs.get_enabled_kem_mechanisms()
        except Exception as exc:
            raise RuntimeError(
                f"liboqs shared library could not be loaded. Please verify OQS_INSTALL_PATH (currently '{self.OQS_INSTALL_PATH}') "
                f"and ensure the liboqs binary is installed/compiled correctly. Internal error: {exc}"
            ) from exc

        return self

try:
    settings = Settings()
except Exception as e:
    print(f"CRITICAL CONFIGURATION ERROR: {e}", file=sys.stderr)
    raise
