"""Administrator service logic."""

from typing import Any, Dict, List, Tuple

from models.db import get_db
from services.base_service import BaseService

ADMIN_REQUESTS_SQL = """
SELECT
    requests.id,
    requests.listing_id,
    requests.buyer_id,
    requests.seller_id,
    requests.status,
    requests.is_locked,
    requests.created_at,
    requests.updated_at,
    listings.title AS listing_title,
    buyers.display_name AS buyer_name,
    sellers.display_name AS seller_name
FROM requests
INNER JOIN listings ON listings.id = requests.listing_id
INNER JOIN users AS buyers ON buyers.id = requests.buyer_id
INNER JOIN users AS sellers ON sellers.id = requests.seller_id
ORDER BY requests.updated_at DESC, requests.id DESC
"""


class AdminService(BaseService):
    """Handle administrator control actions."""

    def get_admin_users(self) -> List[Dict[str, Any]]:
        """Get users for administrator view."""

        db = get_db()
        users = db.execute(
            """
            SELECT
                id,
                display_name,
                email,
                role,
                is_locked,
                preferred_contact_method,
                created_at
            FROM users
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
        return [self._serialize_admin_user(row) for row in users]

    def get_admin_listings(self) -> List[Dict[str, Any]]:
        """Get listings for administrator view."""

        db = get_db()
        listings = db.execute(
            """
            SELECT
                listings.id,
                listings.title,
                listings.price,
                listings.condition,
                listings.status,
                listings.created_at,
                categories.name AS category_name,
                users.id AS seller_id,
                users.display_name AS seller_name
            FROM listings
            INNER JOIN categories ON categories.id = listings.category_id
            INNER JOIN users ON users.id = listings.seller_id
            ORDER BY listings.created_at DESC, listings.id DESC
            """
        ).fetchall()
        return [self._serialize_admin_listing(row) for row in listings]

    def get_admin_requests(self) -> List[Dict[str, Any]]:
        """Get request records for administrator view."""

        db = get_db()
        requests = db.execute(ADMIN_REQUESTS_SQL).fetchall()
        return [self._serialize_admin_request(row) for row in requests]

    def delete_inappropriate_listing(self, listing_id: int) -> Tuple[bool, str]:
        """Delete a listing and its dependent moderation records."""

        db = get_db()
        listing_row = db.execute(
            "SELECT id FROM listings WHERE id = ?",
            (listing_id,),
        ).fetchone()
        if listing_row is None:
            return False, "Listing not found."

        request_rows = db.execute(
            "SELECT id FROM requests WHERE listing_id = ?",
            (listing_id,),
        ).fetchall()
        request_ids = [row["id"] for row in request_rows]

        # Remove child records first because the schema intentionally keeps foreign keys strict.
        if request_ids:
            placeholders = ", ".join(["?"] * len(request_ids))
            db.execute(
                "DELETE FROM reviews WHERE request_id IN ({0})".format(placeholders),
                request_ids,
            )
            db.execute(
                "DELETE FROM requests WHERE id IN ({0})".format(placeholders),
                request_ids,
            )

        db.execute("DELETE FROM favorite_list WHERE listing_id = ?", (listing_id,))
        db.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
        db.commit()
        return True, "Listing deleted successfully."

    def get_admin_completed_requests(self) -> None:
        """Get completed request records for administrator view."""

        raise NotImplementedError

    def lock_user_account(self) -> None:
        """Lock a user account."""

        raise NotImplementedError

    def lock_request_record(self, request_id: int) -> Tuple[bool, str]:
        """Lock a request record."""

        db = get_db()
        request = db.execute(
            "SELECT id, is_locked FROM requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        if request is None:
            return False, "Request record not found."

        if request["is_locked"]:
            return True, "Request record is already locked."

        db.execute(
            """
            UPDATE requests
            SET is_locked = 1, updated_at = datetime('now')
            WHERE id = ?
            """,
            (request_id,),
        )
        db.commit()
        return True, "Request record locked for review."

    @staticmethod
    def _serialize_admin_request(row) -> Dict[str, Any]:
        """Convert an admin request row to template-friendly values."""

        request = dict(row)
        request["status_label"] = str(request["status"]).title()
        request["lock_status_label"] = "Locked" if request["is_locked"] else "Open"
        request["created_at_label"] = str(request["created_at"]).replace("T", " ")[:16]
        request["updated_at_label"] = str(request["updated_at"]).replace("T", " ")[:16]
        return request

    @staticmethod
    def _serialize_admin_listing(row) -> Dict[str, Any]:
        """Convert an admin listing row to template-friendly values."""

        listing = dict(row)
        listing["condition_label"] = str(listing["condition"]).title()
        listing["status_label"] = str(listing["status"]).title()
        listing["price_label"] = "{0:.2f}".format(listing["price"])
        listing["created_at_label"] = str(listing["created_at"]).replace("T", " ")[:16]
        return listing

    @staticmethod
    def _serialize_admin_user(row) -> Dict[str, Any]:
        """Convert an admin user row to template-friendly values."""

        user = dict(row)
        user["role_label"] = str(user["role"]).title()
        user["preferred_contact_method_label"] = str(user["preferred_contact_method"]).title()
        user["account_status_label"] = "Locked" if user["is_locked"] else "Active"
        user["created_at_label"] = str(user["created_at"]).replace("T", " ")[:16]
        return user


admin_service = AdminService()
