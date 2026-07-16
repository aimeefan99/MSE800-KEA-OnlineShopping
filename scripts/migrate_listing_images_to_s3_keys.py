"""Normalize listing image references after uploading legacy files to S3."""

import sqlite3

from config import Config


def main() -> None:
    """Strip the legacy uploads/ prefix so image values match S3 object keys."""

    Config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(Config.DATABASE_PATH)
    try:
        connection.execute(
            """
            UPDATE listings
            SET image_url = REPLACE(image_url, 'uploads/', '')
            WHERE image_url LIKE 'uploads/%'
            """
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
