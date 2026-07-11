"""Listing service logic."""

from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, Tuple

from werkzeug.datastructures import FileStorage

from models.db import get_db
from models.factory import ListingFactory
from services.base_service import BaseService
from services.image_storage_service import image_storage_service
from utils.constants import (
    CONTACT_METHOD_EMAIL,
    CONTACT_METHOD_PHONE,
    LISTING_CONDITIONS,
    LISTING_STATUSES,
    LISTING_STATUS_AVAILABLE,
)
from utils.status_badges import listing_status_badge_class

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
CATEGORY_SEARCH_ALIASES = {
    "Electronics": [
        "camera",
        "phone",
        "iphone",
        "laptop",
        "console",
        "controller",
        "tv",
    ],
    "Clothing & Fashion": [
        "clothing",
        "clothes",
        "cloting",
        "fashion",
        "shoes",
        "boots",
        "skirt",
    ],
}
CONDITION_OPTIONS = LISTING_CONDITIONS
STATUS_OPTIONS = LISTING_STATUSES
LEGACY_CONDITION_MAP = {
    "like new": "used",
    "good": "used",
    "fair": "used",
}
LISTING_DETAIL_SQL = """
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
"""
INSERT_LISTING_SQL = """
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
"""


class ListingService(BaseService):
    """Handle listing-related business logic."""

    def get_user_listings(self, user_id: int) -> List[Dict[str, Any]]:
        """Return all listings created by one marketplace user."""

        listings = get_db().execute(
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
                users.display_name AS seller_name
            FROM listings
            INNER JOIN categories ON categories.id = listings.category_id
            INNER JOIN users ON users.id = listings.seller_id
            WHERE listings.seller_id = ?
            ORDER BY listings.created_at DESC, listings.id DESC
            """,
            (user_id,),
        ).fetchall()
        return [self._serialize_listing_row(listing) for listing in listings]

    def get_category_options(self) -> List[Dict[str, Any]]:
        """Get available category options for listing forms."""
        # Seed the category table once so the form has valid options to render.
        self._ensure_default_categories()
        db = get_db()
        categories = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        return [dict(category) for category in categories]

    def get_search_interest_category_ids(self, keyword: str) -> List[int]:
        """Return category ids inferred from a search keyword."""

        normalized_keyword = keyword.strip().lower()
        if not normalized_keyword:
            return []

        self._ensure_default_categories()
        matched_category_names = [
            category_name
            for category_name, aliases in CATEGORY_SEARCH_ALIASES.items()
            if self._keyword_matches_category(normalized_keyword, category_name, aliases)
        ]
        if not matched_category_names:
            return []

        placeholders = ", ".join("?" for _ in matched_category_names)
        categories = get_db().execute(
            "SELECT id FROM categories WHERE name IN ({0})".format(placeholders),
            matched_category_names,
        ).fetchall()
        return [int(category["id"]) for category in categories]

    @staticmethod
    def get_condition_options() -> List[str]:
        """Get allowed listing condition values."""
        return CONDITION_OPTIONS

    @staticmethod
    def get_status_options() -> List[str]:
        """Get allowed listing status values."""
        return STATUS_OPTIONS

    @staticmethod
    def _keyword_matches_category(
        keyword: str,
        category_name: str,
        aliases: List[str],
    ) -> bool:
        """Return whether a search keyword points to a category."""

        category_label = category_name.lower()
        return keyword in category_label or any(alias in keyword for alias in aliases)

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

        image_url = image_storage_service.save_listing_image(image_file)
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
        price: float,
        status: str,
        image_file: Optional[FileStorage] = None,
    ) -> bool:
        """Update an item's details, but only if the user making the request is the owner!"""
        if status not in STATUS_OPTIONS or condition not in CONDITION_OPTIONS:
            return False

        if price <= 0:
            return False

        if not self._category_exists(str(category_id)):
            return False

        db = get_db()

        # Ownership Safety Check using the class's built-in get_listing_detail method
        item = self.get_listing_detail(listing_id)
        if not item or item["seller_id"] != user_id:
            return False

        image_url = item["image_url"]
        # Keep the current photo unless the seller uploads a replacement image.
        if image_file is not None and image_file.filename:
            image_storage_service.delete_listing_image(image_url)
            image_url = image_storage_service.save_listing_image(image_file)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            """
            UPDATE listings
            SET
                category_id = ?,
                image_url = ?,
                title = ?,
                description = ?,
                condition = ?,
                price = ?,
                status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                category_id,
                image_url,
                title,
                description,
                condition,
                price,
                status,
                now_str,
                listing_id,
            )
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

        image_storage_service.delete_listing_image(item["image_url"])
        db.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
        db.commit()
        return True

    def browse_listings(self, filters: Optional[Mapping[str, str]] = None) -> List[Dict[str, Any]]:
        """Return available listings for the public browse page."""
        db = get_db()
        where_clause, query_parameters = self._build_browse_filter_query(filters or {})

        listings = db.execute(
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
                users.display_name AS seller_name
            FROM listings
            INNER JOIN categories ON categories.id = listings.category_id
            INNER JOIN users ON users.id = listings.seller_id
            WHERE {where_clause}
            ORDER BY listings.created_at DESC, listings.id DESC
            """.format(where_clause=where_clause),
            query_parameters,
        ).fetchall()
        return [self._serialize_listing_row(listing) for listing in listings]

    def _build_browse_filter_query(self, filters: Mapping[str, str]) -> Tuple[str, List[Any]]:
        """Build the listing browse WHERE clause and parameter list."""
        where_clauses = ["listings.status = ?"]
        query_parameters: List[Any] = []
        query_parameters.append(LISTING_STATUS_AVAILABLE)

        self._add_keyword_filter(filters, where_clauses, query_parameters)
        self._add_category_filter(filters, where_clauses, query_parameters)
        self._add_condition_filter(filters, where_clauses, query_parameters)
        self._add_price_filters(filters, where_clauses, query_parameters)

        return " AND ".join(where_clauses), query_parameters

    @staticmethod
    def _add_keyword_filter(
        filters: Mapping[str, str],
        where_clauses: List[str],
        query_parameters: List[Any],
    ) -> None:
        """Add keyword matching across listing title, description, and category."""
        keyword = filters.get("keyword", "").strip()
        if not keyword:
            return

        where_clauses.append(
            """
            (
                listings.title LIKE ?
                OR listings.description LIKE ?
                OR categories.name LIKE ?
            )
            """
        )
        search_term = "%{0}%".format(keyword)
        query_parameters.extend([search_term, search_term, search_term])

    @staticmethod
    def _add_category_filter(
        filters: Mapping[str, str],
        where_clauses: List[str],
        query_parameters: List[Any],
    ) -> None:
        """Add a category filter when the submitted category id is numeric."""
        category_id = filters.get("category_id", "").strip()
        if category_id.isdigit():
            where_clauses.append("listings.category_id = ?")
            query_parameters.append(int(category_id))

    @staticmethod
    def _add_condition_filter(
        filters: Mapping[str, str],
        where_clauses: List[str],
        query_parameters: List[Any],
    ) -> None:
        """Add a condition filter when the value is supported."""
        condition = filters.get("condition", "").strip()
        if condition in CONDITION_OPTIONS:
            where_clauses.append("listings.condition = ?")
            query_parameters.append(condition)

    def _add_price_filters(
        self,
        filters: Mapping[str, str],
        where_clauses: List[str],
        query_parameters: List[Any],
    ) -> None:
        """Add minimum and maximum price filters when values are valid."""
        min_price = self._parse_price_filter(filters.get("min_price", ""))
        if min_price is not None:
            where_clauses.append("listings.price >= ?")
            query_parameters.append(min_price)

        max_price = self._parse_price_filter(filters.get("max_price", ""))
        if max_price is not None:
            where_clauses.append("listings.price <= ?")
            query_parameters.append(max_price)

    def get_listing_detail(self, listing_id: int) -> Optional[Dict[str, Any]]:
        """Return one listing detail record for the detail page."""
        db = get_db()
        listing = db.execute(
            LISTING_DETAIL_SQL,
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
    def _insert_listing(listing) -> int:
        """Insert a listing record and return its id."""
        db = get_db()
        timestamp = datetime.utcnow().isoformat()
        cursor = db.execute(
            INSERT_LISTING_SQL,
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

    @staticmethod
    def _parse_price_filter(value: str) -> Optional[float]:
        """Return a valid non-negative price filter or ignore invalid input."""
        try:
            price = float(value)
        except (TypeError, ValueError):
            return None
        if price < 0:
            return None
        return price

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
        listing["status_label"] = listing["status"].title()
        listing["status_badge_class"] = listing_status_badge_class(listing["status"])
        listing["price_label"] = "{0:.2f}".format(listing["price"])
        seller_contact_method = listing.get("seller_contact_method")
        
        if seller_contact_method == CONTACT_METHOD_PHONE:
            listing["seller_contact_method_label"] = "Phone"
            listing["seller_contact_value"] = listing.get("seller_phone_number") or "Not provided"
        elif seller_contact_method == CONTACT_METHOD_EMAIL:
            listing["seller_contact_method_label"] = "Email"
            listing["seller_contact_value"] = listing.get("seller_email") or "Not provided"
        return listing


listing_service = ListingService()
