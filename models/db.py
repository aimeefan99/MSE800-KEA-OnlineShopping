"""Database connection helpers using a singleton manager."""

import sqlite3

from flask import current_app, g


class DatabaseManager:
    """Manage SQLite connections through a shared singleton instance."""

    _instance = None

    def __new__(cls):
        """Create the singleton instance once."""

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """Return a database connection for the current request."""

        if "db" not in g:
            g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_connection(self) -> None:
        """Close the request database connection if it exists."""

        db = g.pop("db", None)
        if db is not None:
            db.close()


def get_db() -> sqlite3.Connection:
    """Return the current request database connection."""

    return DatabaseManager().get_connection()


def close_db(error=None) -> None:
    """Close the request database connection wrapper."""

    _ = error
    DatabaseManager().close_connection()
