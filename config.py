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
    UPLOAD_FOLDER = Path(
        os.getenv("UPLOAD_FOLDER", str(INSTANCE_DIR / "uploads"))
    )
    LEGACY_UPLOAD_FOLDER = Path(
        os.getenv("LEGACY_UPLOAD_FOLDER", str(BASE_DIR / "static" / "uploads"))
    )
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "5001"))
    DEBUG = _to_bool(os.getenv("FLASK_DEBUG"), True)
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash")
    AI_REQUEST_TIMEOUT_SECONDS = int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "90"))
    AI_IMAGE_MAX_DIMENSION = int(os.getenv("AI_IMAGE_MAX_DIMENSION", "960"))
