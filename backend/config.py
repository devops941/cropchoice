import os
from pathlib import Path
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # Application
    APP_ENV: str = Field(default="development")
    APP_HOST: str = Field(default="127.0.0.1")
    APP_PORT: int = Field(default=8000)
    LOG_LEVEL: str = Field(default="INFO")
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173")

    # MongoDB Atlas
    MONGODB_URI: str = Field(...)
    MONGODB_DB_NAME: str = Field(default="cropchoice")
    MONGODB_TEST_DB_NAME: str = Field(default="cropchoice_test")
    MONGODB_TIMEOUT_MS: int = Field(default=8000)

    # Auth
    JWT_SECRET: str = Field(...)
    JWT_ACCESS_MINUTES: int = Field(default=60)
    JWT_REFRESH_DAYS: int = Field(default=7)
    MAX_FAILED_LOGINS: int = Field(default=5)
    LOCKOUT_MINUTES: int = Field(default=15)
    ADMIN_EMAIL: str = Field(default="admin@cropchoice.local")
    ADMIN_PASSWORD: str = Field(default="Admin@CropChoice2026!")

    # Defaults
    SIM_DEFAULT_RUNS: int = Field(default=5000)
    SIM_SEED: int = Field(default=42)
    MAX_SHARE_DEFAULT: float = Field(default=0.4)
    SOIL_EXCLUSION_THRESHOLD: float = Field(default=0.3)

    # File paths
    REPORT_DIR: str = Field(default=str(BACKEND_DIR / "outputs" / "reports"))
    UPLOAD_DIR: str = Field(default=str(BACKEND_DIR / "data" / "uploads"))
    CONFIG_DIR: str = Field(default=str(BACKEND_DIR / "config"))
    MAX_UPLOAD_MB: int = Field(default=10)

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("MONGODB_URI")
    @classmethod
    def validate_mongodb_uri(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("MONGODB_URI cannot be empty. Please configure your Atlas URI in .env")
        if "<" in v or ">" in v or "<db_user>" in v or "<cluster-host>" in v:
            raise ValueError(
                "MONGODB_URI contains placeholder brackets '<...>'; "
                "replace them with your real MongoDB Atlas credentials in .env"
            )
        if not v.startswith("mongodb://") and not v.startswith("mongodb+srv://"):
            raise ValueError("MONGODB_URI must begin with 'mongodb://' or 'mongodb+srv://'")
        return v.strip()

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("JWT_SECRET is required. Generate a long random secret in .env")
        if "change-me" in v.lower() and len(v) < 20:
            raise ValueError("JWT_SECRET still contains placeholder 'change-me'. Provide a secure secret in .env")
        if len(v.strip()) < 16:
            raise ValueError("JWT_SECRET must be at least 16 characters long.")
        return v.strip()

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


_settings_instance = None

def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
