from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Craque Do Jogo Store"
    SECRET_KEY: str  # obrigatório — gere com: python -c "import secrets; print(secrets.token_urlsafe(64))"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = "/opt/craque-do-jogo/store.db"

    # Pagar.me
    PAGARME_API_KEY: Optional[str] = None
    PAGARME_PIX_KEY: Optional[str] = None

    # Admin seed (só cria admin se definido)
    ADMIN_EMAIL: str = "admin@craquedojogo.com.br"
    ADMIN_PASSWORD: Optional[str] = None

    # CORS — separe por vírgula no .env
    CORS_ORIGINS: list[str] = [
        "https://craquedojogostore.com.br",
        "https://www.craquedojogostore.com.br",
        "http://localhost:5173",
        "http://localhost:5051",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
