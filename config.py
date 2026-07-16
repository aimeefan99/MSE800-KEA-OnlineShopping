"""Application configuration for the second-hand trading platform."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

INSTANCE_DIR = BASE_DIR / "instance"


def _to_bool(value: str, default: bool) -> bool:
    """Convert a string environment value into a boolean flag."""

    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Base configuration values."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_PATH = Path(
        os.getenv("DATABASE_PATH", str(INSTANCE_DIR / "app.db"))
    )
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "").strip()
    S3_REGION = os.getenv("S3_REGION", "").strip()
    S3_PUBLIC_BASE_URL = os.getenv("S3_PUBLIC_BASE_URL", "").strip().rstrip("/")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "").strip()
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "5001"))
    DEBUG = _to_bool(os.getenv("FLASK_DEBUG"), True)
    # Cache static assets so shared UI images like the site logo are reused
    # across page navigations instead of being revalidated every time.
    SEND_FILE_MAX_AGE_DEFAULT = int(
        os.getenv("STATIC_FILE_MAX_AGE_SECONDS", "604800")
    )
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash")
    AI_REQUEST_TIMEOUT_SECONDS = int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "90"))
    AI_IMAGE_MAX_DIMENSION = int(os.getenv("AI_IMAGE_MAX_DIMENSION", "960"))
