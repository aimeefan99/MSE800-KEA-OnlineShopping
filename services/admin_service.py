"""Administrator service logic."""

from typing import Any, Dict, List, Mapping, Optional, Tuple

from models.db import get_db
from services.base_service import BaseService
from utils.constants import (
    LISTING_STATUS_AVAILABLE,
    LISTING_STATUSES,
    REQUEST_STATUS_COMPLETED,
    REQUEST_STATUSES,
    ROLE_ADMIN,
)
from utils.status_badges import (
    listing_status_badge_class,
    lock_status_badge_class,
    request_status_badge_class,
)

ADMIN_REQUESTS_SQL = """
SELECT
    requests.id,
    requests.listing_id,
    requests.buyer_id,
    requests.seller_id,
    requests.status,
    requests.is_locked,
    requests.message,
    requests.created_at,
    requests.updated_at,
    listings.title AS listing_title,
    listings.price AS listing_price,
    buyers.display_name AS buyer_name,
    sellers.display_name AS seller_name
FROM requests
INNER JOIN listings ON listings.id = requests.listing_id
INNER JOIN users AS buyers ON buyers.id = requests.buyer_id
INNER JOIN users AS sellers ON sellers.id = requests.seller_id
{where_clause}
ORDER BY requests.updated_at DESC, requests.id DESC
"""


class AdminService(BaseService):
    """Handle administrator control actions."""

    def get_admin_summary(self) -> Dict[str, int]:
        """Get high-level platform activity counts for admin pages."""

        db = get_db()
        row = db.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM users) AS total_users,
                (SELECT COUNT(*) FROM users WHERE is_locked = 1) AS locked_users,
                (
                    SELECT COUNT(*)
                    FROM listings
                    WHERE status = ?
                ) AS active_listings,
                (
                    SELECT COUNT(*)
                    FROM requests
                    WHERE status = ?
                ) AS completed_requests
            """,
            (LISTING_STATUS_AVAILABLE, REQUEST_STATUS_COMPLETED),
        ).fetchone()
        return {
            "total_users": row["total_users"],
            "locked_users": row["locked_users"],
            "active_listings": row["active_listings"],
            "completed_requests": row["completed_requests"],
        }

    def get_admin_users(
        self,
        filters: Optional[Mapping[str, str]] = None,
    ) -> List[Dict[str, Any]]:
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
        serialized_users = [self._serialize_admin_user(row) for row in users]
        return self._filter_admin_users(serialized_users, filters or {})

    def get_admin_listings(
        self,
        filters: Optional[Mapping[str, str]] = None,
    ) -> List[Dict[str, Any]]:
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
        serialized_listings = [self._serialize_admin_listing(row) for row in listings]
        return self._filter_admin_listings(serialized_listings, filters or {})

    def get_admin_requests(
        self,
        filters: Optional[Mapping[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get request records for administrator view."""

        requests = self._get_admin_request_rows("", [])
        return self._filter_admin_requests(requests, filters or {})

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

    def get_admin_completed_requests(
        self,
        filters: Optional[Mapping[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get completed request records for administrator view."""

        requests = self._get_admin_request_rows(
            "WHERE requests.status = ?",
            [REQUEST_STATUS_COMPLETED],
        )
        return self._filter_admin_requests(requests, filters or {})

    @staticmethod
    def get_listing_status_filter_options() -> List[Dict[str, str]]:
        """Get listing status values for admin filters."""

        return [
            {"value": status, "label": status.title()}
            for status in LISTING_STATUSES
        ]

    @staticmethod
    def get_request_status_filter_options() -> List[Dict[str, str]]:
        """Get request status values for admin filters."""

        return [
            {"value": status, "label": status.title()}
            for status in REQUEST_STATUSES
        ]

    def get_listing_category_filter_options(self) -> List[Dict[str, str]]:
        """Get categories that currently have admin-visible listings."""

        db = get_db()
        categories = db.execute(
            """
            SELECT DISTINCT categories.name
            FROM listings
            INNER JOIN categories ON categories.id = listings.category_id
            ORDER BY categories.name
            """
        ).fetchall()
        return [
            {"value": row["name"], "label": row["name"]}
            for row in categories
        ]

    def lock_user_account(self, user_id: int) -> Tuple[bool, str]:
        """Lock a user account."""

        return self._set_user_lock(user_id, True)

    def unlock_user_account(self, user_id: int) -> Tuple[bool, str]:
        """Unlock a user account."""

        return self._set_user_lock(user_id, False)

    @staticmethod
    def _set_user_lock(user_id: int, should_lock: bool) -> Tuple[bool, str]:
        """Update the lock state for a marketplace user account."""

        db = get_db()
        user = db.execute(
            "SELECT id, role, is_locked FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if user is None:
            return False, "User account not found."

        if user["role"] == ROLE_ADMIN:
            return False, "Administrator accounts cannot be changed from this page."

        if should_lock and user["is_locked"]:
            return True, "User account is already locked."

        if not should_lock and not user["is_locked"]:
            return True, "User account is already active."

        lock_value = 1 if should_lock else 0
        db.execute(
            """
            UPDATE users
            SET is_locked = ?
            WHERE id = ?
            """,
            (lock_value, user_id),
        )
        db.commit()
        if should_lock:
            return True, "User account locked."
        return True, "User account unlocked."

    def lock_request_record(self, request_id: int) -> Tuple[bool, str]:
        """Lock a request record."""

        return self._set_request_lock(request_id, True)

    def unlock_request_record(self, request_id: int) -> Tuple[bool, str]:
        """Unlock a request record."""

        return self._set_request_lock(request_id, False)

    @staticmethod
    def _set_request_lock(request_id: int, should_lock: bool) -> Tuple[bool, str]:
        """Update the review lock state for a request record."""

        db = get_db()
        request = db.execute(
            "SELECT id, is_locked FROM requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        if request is None:
            return False, "Request record not found."

        if should_lock and request["is_locked"]:
            return True, "Request record is already locked."

        if not should_lock and not request["is_locked"]:
            return True, "Request record is already open."

        lock_value = 1 if should_lock else 0
        db.execute(
            """
            UPDATE requests
            SET is_locked = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (lock_value, request_id),
        )
        db.commit()
        if should_lock:
            return True, "Request record locked for review."
        return True, "Request record unlocked."

    def _get_admin_request_rows(
        self,
        where_clause: str,
        parameters: List[Any],
    ) -> List[Dict[str, Any]]:
        """Get request rows for administrator monitoring pages."""

        db = get_db()
        requests = db.execute(
            ADMIN_REQUESTS_SQL.format(where_clause=where_clause),
            parameters,
        ).fetchall()
        return [self._serialize_admin_request(row) for row in requests]

    @staticmethod
    def _serialize_admin_request(row) -> Dict[str, Any]:
        """Convert an admin request row to template-friendly values."""

        request = dict(row)
        request["status_label"] = str(request["status"]).title()
        request["lock_status_label"] = "Locked" if request["is_locked"] else "Open"
        request["status_badge_class"] = request_status_badge_class(
            request["status"],
        )
        request["lock_badge_class"] = lock_status_badge_class(request["is_locked"])
        request["listing_price_label"] = "{0:.2f}".format(request["listing_price"])
        request["created_at_label"] = str(request["created_at"]).replace("T", " ")[:16]
        request["updated_at_label"] = str(request["updated_at"]).replace("T", " ")[:16]
        return request

    @staticmethod
    def _serialize_admin_listing(row) -> Dict[str, Any]:
        """Convert an admin listing row to template-friendly values."""

        listing = dict(row)
        listing["condition_label"] = str(listing["condition"]).title()
        listing["status_label"] = str(listing["status"]).title()
        listing["status_badge_class"] = listing_status_badge_class(
            listing["status"],
        )
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
        user["role_badge_class"] = (
            "text-bg-primary" if user["role"] == ROLE_ADMIN else "text-bg-light border"
        )
        user["account_status_badge_class"] = (
            "text-bg-danger" if user["is_locked"] else "text-bg-success"
        )
        user["created_at_label"] = str(user["created_at"]).replace("T", " ")[:16]
        return user

    @staticmethod
    def _filter_admin_users(
        users: List[Dict[str, Any]],
        filters: Mapping[str, str],
    ) -> List[Dict[str, Any]]:
        """Filter admin users by role and lock state."""

        role_filter = filters.get("role", "")
        status_filter = filters.get("status", "")
        filtered_users = users
        if role_filter:
            filtered_users = [
                user for user in filtered_users if user["role"] == role_filter
            ]
        if status_filter == "locked":
            filtered_users = [user for user in filtered_users if user["is_locked"]]
        elif status_filter == "active":
            filtered_users = [
                user for user in filtered_users if not user["is_locked"]
            ]
        return filtered_users

    @staticmethod
    def _filter_admin_listings(
        listings: List[Dict[str, Any]],
        filters: Mapping[str, str],
    ) -> List[Dict[str, Any]]:
        """Filter admin listings by status and category."""

        status_filter = filters.get("status", "")
        category_filter = filters.get("category", "")
        filtered_listings = listings
        if status_filter:
            filtered_listings = [
                listing
                for listing in filtered_listings
                if listing["status"] == status_filter
            ]
        if category_filter:
            filtered_listings = [
                listing
                for listing in filtered_listings
                if listing["category_name"] == category_filter
            ]
        return filtered_listings

    @staticmethod
    def _filter_admin_requests(
        requests: List[Dict[str, Any]],
        filters: Mapping[str, str],
    ) -> List[Dict[str, Any]]:
        """Filter admin requests by status and lock state."""

        status_filter = filters.get("status", "")
        lock_filter = filters.get("lock", "")
        filtered_requests = requests
        if status_filter:
            filtered_requests = [
                request
                for request in filtered_requests
                if request["status"] == status_filter
            ]
        if lock_filter == "locked":
            filtered_requests = [
                request for request in filtered_requests if request["is_locked"]
            ]
        elif lock_filter == "open":
            filtered_requests = [
                request for request in filtered_requests if not request["is_locked"]
            ]
        return filtered_requests


admin_service = AdminService()
