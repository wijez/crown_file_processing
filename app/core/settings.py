import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # App
    APP_NAME: str = os.environ.get("APP_NAME", "FastAPI")
    APP_DESCRIPTION: str = os.environ.get("APP_DESCRIPTION", "")
    APP_VERSION: str = os.environ.get("APP_VERSION", "0.1.0")
    APP_HOST: str = os.environ.get("APP_HOST", "localhost")
    APP_PORT: int = os.environ.get("APP_PORT", 8000)
    BASE_API_SLUG: str = os.environ.get("BASE_API_SLUG", "/api")
    DEBUG: bool = bool(os.environ.get("DEBUG", False))

    # middleware
    ALLOW_ORIGINS: list

    # Postgresql Database Config
    POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", 'localhost')
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", 'postgres')
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", 'portgasDace')
    POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", 'crown-file-processing')
    DATABASE_URI: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # App Secret Key
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "8deadce9449770680910741063cd0a3fe0acb62a8978661f421bbcbb66dc41f1")

    # JWT Secret
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "649fb93ef34e4fdf4187709c84d643dd61ce730d91856418fdcf563f895ea40f")
    ALGORITHM: str = os.environ.get("ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    REFRESH_TOKEN_EXPIRE_HOURS: int = os.environ.get("REFRESH_TOKEN_EXPIRE_HOURS", "5")
    REFRESH_TOKEN_COOKIE_NAME: str = os.environ.get("REFRESH_TOKEN_COOKIE_NAME", "fastapi_cookie")

    # Email Config
    MAIL_USER: str = os.environ.get("MAIL_USER")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD")
    MAIL_PORT: int = os.environ.get("MAIL_PORT", 465)
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_SSL_TLS: bool = os.environ.get("MAIL_SSL_TLS", True)
    MAIL_STARTTLS: bool = os.environ.get("MAIL_STARTTLS", False)
    VALIDATE_CERTS: bool = os.environ.get("VALIDATE_CERTS", True)

    OPA_SERVER: str = os.environ.get("OPA_SERVER", "localhost")
    OPA_SERVER_PORT: str = os.environ.get("OPA_SERVER_PORT", "8181")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
