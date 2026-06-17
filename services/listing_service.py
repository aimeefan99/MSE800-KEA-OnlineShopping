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
    "Home & Living",
    "Clothing & Fashion",
    "Books & Media",
    "Sports & Outdoors",
    "Beauty & Health",
    "Hobbies & Toys",
    "Vehicles & Bicycles",
    "Other",
]
CONDITION_OPTIONS = ["new", "used"]
LEGACY_CONDITION_MAP = {
    "like new": "used",
    "good": "used",
    "fair": "used",
}


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

    def edit_listing(
        self,
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

        # Ownership Safety Check using the class's built-in get_listing_detail method
        item = self.get_listing_detail(listing_id)
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

    def delete_listing(self, listing_id: int, user_id: int) -> bool:
        """Permanently remove an item, but only if the user making the request is the owner!"""
        db = get_db()

        # Ownership Safety Check using the class's built-in get_listing_detail method
        item = self.get_listing_detail(listing_id)
        if not item or item["seller_id"] != user_id:
            return False

        db.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
        db.commit()
        return True

    def browse_listings(self, keyword: str = "") -> List[Dict[str, Any]]:
        """Return available listings for the public browse page."""
        db = get_db()
        keyword = keyword.strip()
        query_parameters = []
        keyword_filter = ""
        if keyword:
            keyword_filter = """
                AND (
                    listings.title LIKE ?
                    OR listings.description LIKE ?
                    OR categories.name LIKE ?
                )
            """
            search_term = "%{0}%".format(keyword)
            query_parameters = [search_term, search_term, search_term]

        listings = db.execute(
            """
            SELECT
                listings.id,
                listings.seller_id,
                listings.title,
                listings.description,
                listings.condition,
                listings.price,
                listings.image_url,
                listings.status,
                listings.created_at,
                categories.name AS category_name,
                users.display_name AS seller_name
            FROM listings
            INNER JOIN categories ON categories.id = listings.category_id
            INNER JOIN users ON users.id = listings.seller_id
            WHERE listings.status = 'available'
            {keyword_filter}
            ORDER BY listings.created_at DESC, listings.id DESC
            """.format(keyword_filter=keyword_filter),
            query_parameters,
        ).fetchall()
        return [self._serialize_listing_row(listing) for listing in listings]

    def get_listing_detail(self, listing_id: int) -> Optional[Dict[str, Any]]:
        """Return one listing detail record for the detail page."""
        db = get_db()
        listing = db.execute(
            """
            SELECT
                listings.id,
                listings.seller_id,
                listings.category_id,
                listings.title,
                listings.description,
                listings.condition,
                listings.price,
                listings.image_url,
                listings.status,
                listings.created_at,
                categories.name AS category_name,
                users.display_name AS seller_name,
                users.preferred_contact_method AS seller_contact_method,
                users.email AS seller_email,
                users.phone_number AS seller_phone_number
            FROM listings
            INNER JOIN categories ON categories.id = listings.category_id
            INNER JOIN users ON users.id = listings.seller_id
            WHERE listings.id = ?
            """,
            (listing_id,),
        ).fetchone()
        if listing is None:
            return None
        return self._serialize_listing_row(listing)

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
        """Insert any missing default categories."""
        db = get_db()
        existing_names = {
            row["name"]
            for row in db.execute("SELECT name FROM categories").fetchall()
        }
        missing_categories = [
            (name,)
            for name in DEFAULT_CATEGORIES
            if name not in existing_names
        ]
        if not missing_categories:
            return

        db.executemany("INSERT INTO categories (name) VALUES (?)", missing_categories)
        db.commit()

    @staticmethod
    def _serialize_listing_row(row) -> Dict[str, Any]:
        """Convert a database row to template-friendly listing data."""
        listing = dict(row)
        listing["condition"] = LEGACY_CONDITION_MAP.get(listing["condition"], listing["condition"])
        listing["condition_label"] = listing["condition"].title()
        listing["price_label"] = "{0:.2f}".format(listing["price"])
        seller_contact_method = listing.get("seller_contact_method")
        
        if seller_contact_method == "phone":
            listing["seller_contact_method_label"] = "Phone"
            listing["seller_contact_value"] = listing.get("seller_phone_number") or "Not provided"
        elif seller_contact_method == "email":
            listing["seller_contact_method_label"] = "Email"
            listing["seller_contact_value"] = listing.get("seller_email") or "Not provided"
        return listing


listing_service = ListingService()
