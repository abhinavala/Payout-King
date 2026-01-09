"""
Application configuration using Pydantic settings.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Payout King"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-env-var"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database (defaults to SQLite for easy setup, can override with env var)
    # SQLite: sqlite:///./payout_king.db
    # PostgreSQL: postgresql://user:pass@localhost:5432/dbname
    DATABASE_URL: str = "sqlite:///./payout_king.db"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Encryption for API tokens
    ENCRYPTION_KEY: str = "change-me-in-production-use-env-var-32-chars-long!!"

    # Tradovate API
    TRADOVATE_API_URL: str = "https://www.tradovate.com"  # Production API
    TRADOVATE_AUTH_URL: str = "https://www.tradovate.com/auth/accesstokenrequest"  # Auth endpoint
    TRADOVATE_WS_URL: str = "wss://www.tradovate.com/ws"  # WebSocket (if available)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

