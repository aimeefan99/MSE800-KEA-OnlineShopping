"""Transaction-related service placeholders for favorites, requests, and reviews."""

from typing import Any, Dict, List, Optional, Tuple

from models.db import get_db
from services.base_service import BaseService

INCOMING_REQUESTS_SQL = """
SELECT
    requests.id,
    requests.listing_id,
    requests.buyer_id,
    requests.seller_id,
    requests.status,
    requests.message,
    requests.created_at,
    requests.updated_at,
    listings.title AS listing_title,
    listings.price AS listing_price,
    listings.status AS listing_status,
    users.display_name AS buyer_name,
    users.email AS buyer_email,
    users.phone_number AS buyer_phone_number,
    users.preferred_contact_method AS buyer_contact_method
FROM requests
INNER JOIN listings ON listings.id = requests.listing_id
INNER JOIN users ON users.id = requests.buyer_id
WHERE requests.seller_id = ?
ORDER BY requests.created_at DESC, requests.id DESC
"""


class TransactionService(BaseService):
    """Handle favorites, requests, and review workflow logic."""

    def view_favorites(self) -> None:
        """Get favorite listings for the current user."""

        raise NotImplementedError

    def add_favorite(self, user_id: int, listing_id: int) -> str:
        """Add a listing to the favorite list."""

        if not self._listing_exists(listing_id):
            return "Listing not found."

        db = get_db()
        existing_favorite = db.execute(
            "SELECT id FROM favorite_list WHERE user_id = ? AND listing_id = ?",
            (user_id, listing_id),
        ).fetchone()
        if existing_favorite is not None:
            return "This listing is already in your favorites."

        # Favorites are stored per-user so the same listing can still be saved by others.
        db.execute(
            """
            INSERT INTO favorite_list (user_id, listing_id, created_at)
            VALUES (?, ?, datetime('now'))
            """,
            (user_id, listing_id),
        )
        db.commit()
        return "Listing added to favorites."

    def remove_favorite(self) -> None:
        """Remove a listing from the favorite list."""

        raise NotImplementedError

    def create_request(
        self,
        buyer_id: int,
        listing_id: int,
        message: str = "",
    ) -> Tuple[bool, str]:
        """Create a purchase request."""

        listing = self._get_listing_for_request(listing_id)
        if listing is None:
            return False, "Listing not found."

        if listing["status"] != "available":
            return False, "This listing is not available for purchase requests."

        seller_id = int(listing["seller_id"])
        if seller_id == buyer_id:
            return False, "You cannot request to buy your own listing."

        if self._has_pending_request(buyer_id, listing_id):
            return False, "You already have a pending request for this listing."

        db = get_db()
        db.execute(
            """
            INSERT INTO requests (
                listing_id,
                buyer_id,
                seller_id,
                status,
                is_locked,
                message,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, 'pending', 0, ?, datetime('now'), datetime('now'))
            """,
            (listing_id, buyer_id, seller_id, message.strip() or None),
        )
        db.commit()
        return True, "Purchase request submitted."

    def incoming_requests(self, seller_id: int) -> List[Dict[str, Any]]:
        """Get incoming requests for a seller."""

        db = get_db()
        requests = db.execute(INCOMING_REQUESTS_SQL, (seller_id,)).fetchall()
        return [self._serialize_incoming_request(request) for request in requests]

    def request_history(self) -> None:
        """Get request history for a user."""

        raise NotImplementedError

    def accept_request(self) -> None:
        """Accept a purchase request."""

        raise NotImplementedError

    def reject_request(self) -> None:
        """Reject a purchase request."""

        raise NotImplementedError

    def complete_request(self) -> None:
        """Complete a purchase request."""

        raise NotImplementedError

    def create_review(self) -> None:
        """Create a review."""

        raise NotImplementedError

    def get_favorite_id(self, user_id: int, listing_id: int) -> Optional[int]:
        """Return the favorite record id when the listing is already saved by the user."""

        db = get_db()
        favorite = db.execute(
            "SELECT id FROM favorite_list WHERE user_id = ? AND listing_id = ?",
            (user_id, listing_id),
        ).fetchone()
        if favorite is None:
            return None
        return int(favorite["id"])

    def get_request_status(self, buyer_id: int, listing_id: int) -> Optional[str]:
        """Return the buyer's latest request status for a listing."""

        db = get_db()
        request = db.execute(
            """
            SELECT status
            FROM requests
            WHERE buyer_id = ? AND listing_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (buyer_id, listing_id),
        ).fetchone()
        if request is None:
            return None
        return str(request["status"])

    @staticmethod
    def _listing_exists(listing_id: int) -> bool:
        """Check whether the requested listing exists before saving it."""

        db = get_db()
        listing = db.execute("SELECT id FROM listings WHERE id = ?", (listing_id,)).fetchone()
        return listing is not None

    @staticmethod
    def _get_listing_for_request(listing_id: int):
        """Fetch listing details needed to validate a purchase request."""

        db = get_db()
        return db.execute(
            "SELECT id, seller_id, status FROM listings WHERE id = ?",
            (listing_id,),
        ).fetchone()

    @staticmethod
    def _has_pending_request(buyer_id: int, listing_id: int) -> bool:
        """Check whether the buyer already has an open request for the item."""

        db = get_db()
        request = db.execute(
            """
            SELECT id
            FROM requests
            WHERE buyer_id = ? AND listing_id = ? AND status = 'pending'
            """,
            (buyer_id, listing_id),
        ).fetchone()
        return request is not None

    @staticmethod
    def _serialize_incoming_request(row) -> Dict[str, Any]:
        """Convert an incoming request row to template-friendly values."""

        request = dict(row)
        request["listing_price_label"] = "{0:.2f}".format(request["listing_price"])
        request["status_label"] = request["status"].title()
        request["listing_status_label"] = request["listing_status"].title()
        if request["buyer_contact_method"] == "phone":
            request["buyer_contact_method_label"] = "Phone"
            request["buyer_contact_value"] = request["buyer_phone_number"] or "Not provided"
        else:
            request["buyer_contact_method_label"] = "Email"
            request["buyer_contact_value"] = request["buyer_email"] or "Not provided"
        return request

transaction_service = TransactionService()
