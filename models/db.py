"""Database connection helpers."""

from flask import current_app, g
import sqlite3


def get_db() -> sqlite3.Connection:
    """Return a database connection for the current request."""

    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None) -> None:
    """Close the request database connection if it exists."""

    _ = error
    db = g.pop("db", None)
    if db is not None:
        db.close()
