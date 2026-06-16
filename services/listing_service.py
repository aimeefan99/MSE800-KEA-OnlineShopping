"""Listing service logic for managing marketplace items."""

from datetime import datetime
from models.db import get_db


def browse_listings(category_id=None, search_query=None):
    """Retrieve all available items from the database with optional filters."""
    db = get_db()
    sql = "SELECT * FROM listings WHERE status = 'available'"
    params = []

    if category_id:
        sql += " AND category_id = ?"
        params.append(category_id)

    if search_query:
        sql += " AND (title LIKE ? OR description LIKE ?)"
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")

    sql += " ORDER BY created_at DESC"
    cursor = db.execute(sql, tuple(params))
    return cursor.fetchall()


def get_listing_detail(listing_id: int):
    """Get everything about one specific item so we can display or edit it."""
    db = get_db()
    cursor = db.execute("SELECT * FROM listings WHERE id = ?", (listing_id,))
    return cursor.fetchone()


def create_listing(
    seller_id: int,
    category_id: int,
    title: str,
    description: str,
    condition: str,
    price: float,
    image_url: str = "placeholder.jpg"
) -> int:
    """Save a brand-new item into our store database."""
    db = get_db()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = db.execute(
        """
        INSERT INTO listings (
            seller_id, category_id, image_url, title, description, condition, price, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'available', ?, ?)
        """,
        (
            seller_id,
            category_id,
            image_url,
            title,
            description,
            condition,
            price,
            now_str,
            now_str
        )
    )
    db.commit()
    return cursor.lastrowid


def edit_listing(
    listing_id: int,
    user_id: int,
    category_id: int,
    title: str,
    description: str,
    condition: str,
    price: float
) -> bool:
    """Update an item's details, but only if the user making the request is the owner!"""
    db = get_db()

    # Ownership Safety Check
    item = get_listing_detail(listing_id)
    if not item or item["seller_id"] != user_id:
        return False

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        """
        UPDATE listings 
        SET category_id = ?, title = ?, description = ?, condition = ?, price = ?, updated_at = ?
        WHERE id = ?
        """,
        (category_id, title, description, condition, price, now_str, listing_id)
    )
    db.commit()
    return True


def delete_listing(listing_id: int, user_id: int) -> bool:
    """Permanently remove an item, but only if the user making the request is the owner!"""
    db = get_db()

    # Ownership Safety Check
    item = get_listing_detail(listing_id)
    if not item or item["seller_id"] != user_id:
        return False

    db.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    db.commit()
    return True