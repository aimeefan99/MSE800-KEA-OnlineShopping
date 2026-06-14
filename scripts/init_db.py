"""Initialize the SQLite database schema."""

from pathlib import Path
import sqlite3

from models.schema import SCHEMA

ROOT = Path(__file__).resolve().parent.parent
INSTANCE_DIR = ROOT / "instance"
DATABASE_PATH = INSTANCE_DIR / "app.db"


def main() -> None:
    """Create the SQLite database and schema."""

    INSTANCE_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
