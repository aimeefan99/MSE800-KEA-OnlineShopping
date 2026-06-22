"""Administrator service logic."""

from typing import Any, Dict, List

from models.db import get_db
from services.base_service import BaseService


class AdminService(BaseService):
    """Handle administrator control actions."""

    def get_admin_users(self) -> None:
        """Get users for administrator view."""

        raise NotImplementedError

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

    def get_admin_requests(self) -> None:
        """Get request records for administrator view."""

        raise NotImplementedError

    def delete_inappropriate_listing(self) -> None:
        """Delete an inappropriate listing."""

        raise NotImplementedError

    def get_admin_completed_requests(self) -> None:
        """Get completed request records for administrator view."""

        raise NotImplementedError

    def lock_user_account(self) -> None:
        """Lock a user account."""

        raise NotImplementedError

    def lock_request_record(self) -> None:
        """Lock a request record."""

        raise NotImplementedError

    @staticmethod
    def _serialize_admin_listing(row) -> Dict[str, Any]:
        """Convert an admin listing row to template-friendly values."""

        listing = dict(row)
        listing["condition_label"] = str(listing["condition"]).title()
        listing["status_label"] = str(listing["status"]).title()
        listing["price_label"] = "{0:.2f}".format(listing["price"])
        listing["created_at_label"] = str(listing["created_at"]).replace("T", " ")[:16]
        return listing


admin_service = AdminService()
