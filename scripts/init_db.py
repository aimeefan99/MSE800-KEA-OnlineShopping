"""Initialize the SQLite database schema."""

import sqlite3

from config import Config
from models.schema import SCHEMA


def main() -> None:
    """Create the SQLite database and schema."""

    Config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(Config.DATABASE_PATH)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
