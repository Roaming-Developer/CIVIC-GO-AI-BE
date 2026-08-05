import os
from functools import lru_cache
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def parse_cors_origins(value: Any) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


CorsOrigins = Annotated[list[str], NoDecode, BeforeValidator(parse_cors_origins)]
DEFAULT_JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "replace-this-development-secret-before-deploying"
)


# Use .env file to override default settings in production
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    project_name: str = os.getenv(
        "PROJECT_NAME", "CIVIC GO AI - Legal Document Analyzer"
    )
    environment: str = os.getenv("ENVIRONMENT", "development")
    api_v1_prefix: str = "/api/v1"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/practice_db",
    )
    jwt_secret_key: str = DEFAULT_JWT_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(
        default=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30), gt=0
    )
    refresh_token_expire_minutes: int = Field(
        default=os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7), gt=0
    )  # 7 days
    backend_cors_origins: CorsOrigins = os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
    aws_access_key_id: str | None = os.getenv("AWS_ACCESS_KEY_ID", None)
    aws_secret_access_key: str | None = os.getenv("AWS_SECRET_ACCESS_KEY", None)
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    s3_bucket_name: str | None = os.getenv("S3_BUCKET_NAME", None)

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if (
            self.environment.lower() in {"production", "prod"}
            and self.jwt_secret_key == DEFAULT_JWT_SECRET_KEY
        ):
            raise ValueError("JWT_SECRET_KEY must be configured in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
