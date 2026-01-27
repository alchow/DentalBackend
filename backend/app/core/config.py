from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, computed_field
from typing import Optional

import os
from urllib.parse import quote_plus

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dental Notes Backend"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8080", "http://localhost:3000"]
    API_KEY: str = os.getenv("API_KEY", "secret-key") # Change in production
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY") # Required for Search
    
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
        
        host_val = self.POSTGRES_SERVER
        # Detect if this is a Cloud SQL connection name (e.g. project:region:instance)
        # or an explicit socket path
        is_cloud_sql = ":" in host_val and "/" not in host_val and host_val not in ["localhost", "127.0.0.1"]
        is_socket = host_val.startswith("/")
        
        if is_socket or is_cloud_sql:
            # Unix Socket (Cloud Run)
            socket_path = host_val
            if not socket_path.startswith("/"):
                socket_path = f"/cloudsql/{socket_path}"
            return f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@/{self.POSTGRES_DB}?host={socket_path}"
        else:
            # TCP (Local)
            # When connecting via Cloud SQL Proxy on localhost, SSL is handled by the proxy.
            # We must explicitly tell asyncpg NOT to try SSL, otherwise the handshake fails.
            return f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?ssl=disable"

    class Config:
        case_sensitive = True

settings = Settings()
