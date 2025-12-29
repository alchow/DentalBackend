from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, computed_field
from typing import Optional

import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dental Notes Backend"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Allow DB_* env vars to override defaults (Cloud Run style)
    POSTGRES_SERVER: str = os.getenv("DB_HOST", "localhost")
    POSTGRES_USER: str = os.getenv("DB_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASS", "postgres")
    POSTGRES_DB: str = os.getenv("DB_NAME", "dental_notes")
    POSTGRES_PORT: int = int(os.getenv("DB_PORT", 5432))
    
    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    class Config:
        case_sensitive = True

settings = Settings()
