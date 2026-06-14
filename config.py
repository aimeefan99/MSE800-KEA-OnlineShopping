"""Application configuration for the second-hand trading platform."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "app.db"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"


class Config:
    """Base configuration values."""

    SECRET_KEY = "dev-secret-key"
    DATABASE_PATH = DATABASE_PATH
    UPLOAD_FOLDER = UPLOAD_FOLDER
