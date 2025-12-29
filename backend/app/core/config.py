from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, computed_field
from typing import Optional

import os
from urllib.parse import quote_plus

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
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        encoded_user = quote_plus(self.POSTGRES_USER)
        encoded_pass = quote_plus(self.POSTGRES_PASSWORD)
        
        if self.POSTGRES_SERVER.startswith("/"):
            # Unix Socket (Cloud Run)
            return f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@/{self.POSTGRES_DB}?host={self.POSTGRES_SERVER}"
        else:
            # TCP (Local)
            return f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True

settings = Settings()
