"""Application configuration for the second-hand trading platform."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "app.db"
UPLOAD_FOLDER = INSTANCE_DIR / "uploads"
LEGACY_UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"


class Config:
    """Base configuration values."""

    SECRET_KEY = "dev-secret-key"
    DATABASE_PATH = DATABASE_PATH
    UPLOAD_FOLDER = UPLOAD_FOLDER
    LEGACY_UPLOAD_FOLDER = LEGACY_UPLOAD_FOLDER
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash")
    AI_REQUEST_TIMEOUT_SECONDS = int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "90"))
    AI_IMAGE_MAX_DIMENSION = int(os.getenv("AI_IMAGE_MAX_DIMENSION", "960"))
