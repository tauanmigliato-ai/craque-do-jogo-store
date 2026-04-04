from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Craque Do Jogo Store"
    SECRET_KEY: str = "craque-do-jogo-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = "/opt/craque-do-jogo/store.db"

    # Pagar.me
    PAGARME_API_KEY: Optional[str] = None
    PAGARME_PIX_KEY: Optional[str] = None

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()