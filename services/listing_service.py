"""Listing service logic."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from models.db import get_db
from models.factory import ListingFactory
from services.base_service import BaseService

DEFAULT_CATEGORIES = [
    "Electronics",
    "Furniture",
    "Books",
    "Clothing",
    "Beauty",
    "Sports",
]
CONDITION_OPTIONS = ["new", "like new", "good", "fair"]


class ListingService(BaseService):
    """Handle listing-related business logic."""

    def get_category_options(self) -> List[Dict[str, Any]]:
        """Get available category options for listing forms."""

        # Seed the category table once so the form has valid options to render.
        self._ensure_default_categories()
        db = get_db()
        categories = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        return [dict(category) for category in categories]

    @staticmethod
    def get_condition_options() -> List[str]:
        """Get allowed listing condition values."""

        return CONDITION_OPTIONS

    def create_listing(
        self,
        seller_id: int,
        form_data: Mapping[str, str],
        image_file: Optional[FileStorage],
    ) -> Tuple[bool, Optional[str], Dict[str, str], Optional[int]]:
        """Create a listing from form input."""

        # Return cleaned form data on failure so the form can be re-rendered.
        cleaned_data = self._clean_listing_data(form_data)
        validation_error = self._validate_listing_data(cleaned_data, image_file)
        if validation_error is not None:
            return False, validation_error, cleaned_data, None

        image_url = self._save_image_file(image_file)
        listing = ListingFactory.create_from_form(
            seller_id=seller_id,
            category_id=int(cleaned_data["category_id"]),
            title=cleaned_data["title"],
            description=cleaned_data["description"],
            condition=cleaned_data["condition"],
            price=float(cleaned_data["price"]),
            image_url=image_url,
        )
        listing_id = self._insert_listing(listing)
        return True, None, cleaned_data, listing_id

    def edit_listing(self) -> None:
        """Edit a listing."""

        raise NotImplementedError

    def delete_listing(self) -> None:
        """Delete a listing."""

        raise NotImplementedError

    def browse_listings(self) -> None:
        """Browse listings."""

        raise NotImplementedError

    def get_listing_detail(self) -> None:
        """Get listing detail."""

        raise NotImplementedError

    @staticmethod
    def _clean_listing_data(form_data: Mapping[str, str]) -> Dict[str, str]:
        """Normalize create listing form values."""

        return {
            "title": form_data.get("title", "").strip(),
            "category_id": form_data.get("category_id", "").strip(),
            "description": form_data.get("description", "").strip(),
            "condition": form_data.get("condition", "").strip(),
            "price": form_data.get("price", "").strip(),
        }

    def _validate_listing_data(
        self,
        cleaned_data: Mapping[str, str],
        image_file: Optional[FileStorage],
    ) -> Optional[str]:
        """Check create listing rules."""

        required_fields = ["title", "category_id", "description", "condition", "price"]
        if not all(cleaned_data[field] for field in required_fields):
            return "Please complete all required fields."

        if image_file is None or not image_file.filename:
            return "Please upload one listing image."

        if cleaned_data["condition"] not in CONDITION_OPTIONS:
            return "Please select a valid item condition."

        if not self._category_exists(cleaned_data["category_id"]):
            return "Please select a valid category."

        try:
            price = float(cleaned_data["price"])
        except ValueError:
            return "Please enter a valid price."

        if price <= 0:
            return "Price must be greater than 0."
        return None

    @staticmethod
    def _save_image_file(image_file: FileStorage) -> str:
        """Save the uploaded image and return its relative path."""

        upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
        upload_folder.mkdir(parents=True, exist_ok=True)

        filename = secure_filename(image_file.filename)
        unique_name = "{0}_{1}".format(uuid4().hex, filename)
        image_path = upload_folder / unique_name
        image_file.save(image_path)
        return "uploads/{0}".format(unique_name)

    @staticmethod
    def _insert_listing(listing) -> int:
        """Insert a listing record and return its id."""

        db = get_db()
        timestamp = datetime.utcnow().isoformat()
        cursor = db.execute(
            """
            INSERT INTO listings (
                seller_id,
                category_id,
                image_url,
                title,
                description,
                condition,
                price,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                listing.seller_id,
                listing.category_id,
                listing.image_url,
                listing.title,
                listing.description,
                listing.condition,
                listing.price,
                listing.status,
                timestamp,
                timestamp,
            ),
        )
        db.commit()
        return int(cursor.lastrowid)

    def _category_exists(self, category_id: str) -> bool:
        """Check whether a category id exists."""

        if not category_id.isdigit():
            return False
        db = get_db()
        category = db.execute(
            "SELECT id FROM categories WHERE id = ?",
            (int(category_id),),
        ).fetchone()
        return category is not None

    def _ensure_default_categories(self) -> None:
        """Insert default categories when the table is empty."""

        db = get_db()
        category_count = db.execute("SELECT COUNT(*) AS count FROM categories").fetchone()["count"]
        if category_count:
            return

        db.executemany(
            "INSERT INTO categories (name) VALUES (?)",
            [(name,) for name in DEFAULT_CATEGORIES],
        )
        db.commit()


listing_service = ListingService()
