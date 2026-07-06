"""Transaction-related service logic for favorites, requests, and reviews."""

from typing import Any, Dict, List, Optional, Tuple

from models.db import get_db
from services.base_service import BaseService
from utils.constants import (
    CONTACT_METHOD_PHONE,
    LISTING_STATUS_AVAILABLE,
    LISTING_STATUS_PENDING,
    REQUEST_STATUS_ACCEPTED,
    REQUEST_STATUS_COMPLETED,
    REQUEST_STATUS_PENDING,
    REQUEST_STATUS_REJECTED,
)

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
OUTGOING_REQUESTS_SQL = """
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
    users.display_name AS seller_name
FROM requests
INNER JOIN listings ON listings.id = requests.listing_id
INNER JOIN users ON users.id = requests.seller_id
WHERE requests.buyer_id = ?
ORDER BY requests.created_at DESC, requests.id DESC
"""


class TransactionService(BaseService):
    """Handle favorites, requests, and review workflow logic."""

    def view_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get favorite listings for the current user."""

        db = get_db()
        favorites = db.execute(
            """
            SELECT
                favorite_list.id,
                favorite_list.listing_id,
                favorite_list.created_at,
                listings.title,
                listings.price,
                listings.image_url,
                listings.condition,
                listings.status
            FROM favorite_list
            INNER JOIN listings ON listings.id = favorite_list.listing_id
            WHERE favorite_list.user_id = ?
            ORDER BY favorite_list.created_at DESC, favorite_list.id DESC
            """,
            (user_id,),
        ).fetchall()
        return [self._serialize_favorite(row) for row in favorites]

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

        if listing["status"] != LISTING_STATUS_AVAILABLE:
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
            VALUES (?, ?, ?, ?, 0, ?, datetime('now'), datetime('now'))
            """,
            (listing_id, buyer_id, seller_id, REQUEST_STATUS_PENDING, message.strip() or None),
        )
        db.commit()
        return True, "Purchase request submitted."

    def incoming_requests(self, seller_id: int) -> List[Dict[str, Any]]:
        """Get incoming requests for a seller."""

        db = get_db()
        requests = db.execute(INCOMING_REQUESTS_SQL, (seller_id,)).fetchall()
        return [
            self._serialize_incoming_request(request, seller_id)
            for request in requests
        ]

    def request_history(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get the current user's sent and received request views for the request hub."""

        db = get_db()
        outgoing_requests = db.execute(OUTGOING_REQUESTS_SQL, (user_id,)).fetchall()
        incoming_requests = db.execute(INCOMING_REQUESTS_SQL, (user_id,)).fetchall()
        return {
            "outgoing_requests": [
                self._serialize_outgoing_request(request, user_id)
                for request in outgoing_requests
            ],
            "incoming_requests": [
                self._serialize_incoming_request(request, user_id)
                for request in incoming_requests
            ],
            "summary": self._get_request_history_summary(user_id),
        }

    @staticmethod
    def _get_request_history_summary(user_id: int) -> Dict[str, int]:
        """Return request and completed transaction counts for the activity hub."""

        db = get_db()
        summary = db.execute(
            """
            SELECT
                COUNT(CASE WHEN buyer_id = ? THEN 1 END) AS sent_request_count,
                COUNT(CASE WHEN seller_id = ? THEN 1 END) AS incoming_request_count,
                COUNT(
                    CASE
                        WHEN status = ? AND (buyer_id = ? OR seller_id = ?)
                        THEN 1
                    END
                ) AS completed_transaction_count
            FROM requests
            WHERE buyer_id = ? OR seller_id = ?
            """,
            (
                user_id,
                user_id,
                REQUEST_STATUS_COMPLETED,
                user_id,
                user_id,
                user_id,
                user_id,
            ),
        ).fetchone()
        return {
            "sent_request_count": int(summary["sent_request_count"]),
            "incoming_request_count": int(summary["incoming_request_count"]),
            "completed_transaction_count": int(summary["completed_transaction_count"]),
        }

    def accept_request(self, seller_id: int, request_id: int) -> Tuple[bool, str]:
        """Accept a purchase request."""

        request, error_message = self._get_authorized_request(seller_id, request_id)
        if error_message is not None:
            return False, error_message

        if request["status"] != REQUEST_STATUS_PENDING:
            return False, "Only pending requests can be accepted."

        if request["listing_status"] != LISTING_STATUS_AVAILABLE:
            return False, "This listing is not available for accepting a request."

        if self._listing_has_accepted_request(int(request["listing_id"])):
            return False, "This listing already has an accepted request."

        self._mark_request_accepted(request_id, int(request["listing_id"]))
        return True, "Purchase request accepted."

    def reject_request(self, seller_id: int, request_id: int) -> Tuple[bool, str]:
        """Reject a purchase request."""

        request, error_message = self._get_authorized_request(seller_id, request_id)
        if error_message is not None:
            return False, error_message

        if request["status"] not in (REQUEST_STATUS_PENDING, REQUEST_STATUS_ACCEPTED):
            return False, "Only pending or accepted requests can be rejected."

        was_accepted = request["status"] == REQUEST_STATUS_ACCEPTED
        self._mark_request_rejected(request_id, int(request["listing_id"]), was_accepted)
        return True, "Purchase request rejected."

    def complete_request(self, buyer_id: int, request_id: int) -> Tuple[bool, str]:
        """Complete a purchase request (buyer only)."""

        request, error_message = self._get_authorized_request_for_buyer(buyer_id, request_id)
        if error_message is not None:
            return False, error_message

        if request["status"] != "accepted":
            return False, "Only accepted requests can be completed."

        self._mark_request_completed(request_id, int(request["listing_id"]))
        return True, "Transaction completed successfully."

    def create_review(
        self,
        reviewer_id: int,
        request_id: Optional[int],
        reviewed_user_id: Optional[int],
        score: Optional[int],
        comment: str = "",
    ) -> Tuple[bool, str]:
        """Create a review."""

        if request_id is None or reviewed_user_id is None or score is None:
            return False, "Please complete all required review fields."

        request = self._get_request_for_action(request_id)
        if request is None:
            return False, "Purchase request not found."

        validation_error = self._validate_review_participants(
            request,
            reviewer_id,
            reviewed_user_id,
            score,
        )
        if validation_error is not None:
            return False, validation_error

        if self._review_exists(request_id, reviewer_id, reviewed_user_id):
            return False, "You have already reviewed this completed transaction."

        db = get_db()
        db.execute(
            """
            INSERT INTO reviews (
                request_id,
                reviewer_id,
                reviewed_user_id,
                score,
                comment,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (request_id, reviewer_id, reviewed_user_id, score, comment.strip() or None),
        )
        db.commit()
        return True, "Review submitted successfully."

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
    def _mark_request_accepted(request_id: int, listing_id: int) -> None:
        """Set the selected request accepted and move the listing to pending."""

        db = get_db()
        db.execute(
            """
            UPDATE requests
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (REQUEST_STATUS_ACCEPTED, request_id),
        )
        db.execute(
            """
            UPDATE listings
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (LISTING_STATUS_PENDING, listing_id),
        )
        db.commit()

    @staticmethod
    def _mark_request_rejected(
        request_id: int,
        listing_id: int,
        was_accepted: bool,
    ) -> None:
        """Set a request rejected and reopen its listing when needed."""

        db = get_db()
        db.execute(
            """
            UPDATE requests
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (REQUEST_STATUS_REJECTED, request_id),
        )
        if was_accepted:
            db.execute(
                """
                UPDATE listings
                SET status = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (LISTING_STATUS_AVAILABLE, listing_id),
            )
        db.commit()

    @staticmethod
    def _mark_request_completed(request_id: int, listing_id: int) -> None:
        """Mark a request as completed and update listing status to sold."""

        db = get_db()
        db.execute(
            """
            UPDATE requests
            SET status = 'completed', updated_at = datetime('now')
            WHERE id = ?
            """,
            (request_id,),
        )
        db.execute(
            """
            UPDATE listings
            SET status = 'sold', updated_at = datetime('now')
            WHERE id = ?
            """,
            (listing_id,),
        )
        # Reject any remaining open requests (pending or accepted) for this listing
        db.execute(
            """
            UPDATE requests
            SET status = 'rejected', updated_at = datetime('now')
            WHERE listing_id = ? AND id != ? AND status IN ('pending', 'accepted')
            """,
            (listing_id, request_id),
        )
        db.commit()

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
            WHERE buyer_id = ? AND listing_id = ? AND status = ?
            """,
            (buyer_id, listing_id, REQUEST_STATUS_PENDING),
        ).fetchone()
        return request is not None

    @staticmethod
    def _get_request_for_action(request_id: int):
        """Fetch request and listing details needed for seller status actions."""

        db = get_db()
        return db.execute(
            """
            SELECT
                requests.id,
                requests.listing_id,
                requests.buyer_id,
                requests.seller_id,
                requests.status,
                requests.is_locked,
                listings.status AS listing_status
            FROM requests
            INNER JOIN listings ON listings.id = requests.listing_id
            WHERE requests.id = ?
            """,
            (request_id,),
        ).fetchone()

    def _get_authorized_request(self, seller_id: int, request_id: int):
        """Return a request row after checking seller ownership and lock status."""

        request = self._get_request_for_action(request_id)
        if request is None:
            return None, "Purchase request not found."

        if int(request["seller_id"]) != seller_id:
            return None, "You can only manage requests for your own listings."

        if request["is_locked"]:
            return None, "This request is locked and cannot be changed."

        return request, None

    def _get_authorized_request_for_buyer(self, buyer_id: int, request_id: int):
        """Return a request row after checking buyer ownership and lock status."""

        request = self._get_request_for_action(request_id)
        if request is None:
            return None, "Purchase request not found."

        if int(request["buyer_id"]) != buyer_id:
            return None, "You can only manage requests you created."

        if request["is_locked"]:
            return None, "This request is locked and cannot be changed."

        return request, None

    @staticmethod
    def _listing_has_accepted_request(listing_id: int) -> bool:
        """Check whether a listing already has an accepted request."""

        db = get_db()
        request = db.execute(
            """
            SELECT id
            FROM requests
            WHERE listing_id = ? AND status = ?
            """,
            (listing_id, REQUEST_STATUS_ACCEPTED),
        ).fetchone()
        return request is not None

    @staticmethod
    def _validate_review_participants(
        request,
        reviewer_id: int,
        reviewed_user_id: int,
        score: int,
    ) -> Optional[str]:
        """Check that a review is allowed for the completed transaction."""

        if request["status"] != REQUEST_STATUS_COMPLETED:
            return "Only completed transactions can be reviewed."

        if score < 1 or score > 5:
            return "Review score must be between 1 and 5."

        buyer_id = int(request["buyer_id"])
        seller_id = int(request["seller_id"])
        if reviewer_id not in (buyer_id, seller_id):
            return "You can only review transactions you participated in."

        expected_reviewed_user_id = seller_id if reviewer_id == buyer_id else buyer_id
        if reviewed_user_id != expected_reviewed_user_id:
            return "You can only review the other user in this transaction."
        return None

    @staticmethod
    def _review_exists(request_id: int, reviewer_id: int, reviewed_user_id: int) -> bool:
        """Check whether this reviewer already reviewed the other party."""

        db = get_db()
        review = db.execute(
            """
            SELECT id
            FROM reviews
            WHERE request_id = ? AND reviewer_id = ? AND reviewed_user_id = ?
            """,
            (request_id, reviewer_id, reviewed_user_id),
        ).fetchone()
        return review is not None

    def _serialize_incoming_request(self, row, current_user_id: int) -> Dict[str, Any]:
        """Convert an incoming request row to template-friendly values."""

        request = dict(row)
        request["listing_price_label"] = "{0:.2f}".format(request["listing_price"])
        request["status_label"] = request["status"].title()
        request["listing_status_label"] = request["listing_status"].title()
        if request["buyer_contact_method"] == CONTACT_METHOD_PHONE:
            request["buyer_contact_method_label"] = "Phone"
            request["buyer_contact_value"] = request["buyer_phone_number"] or "Not provided"
        else:
            request["buyer_contact_method_label"] = "Email"
            request["buyer_contact_value"] = request["buyer_email"] or "Not provided"
        self._attach_review_state(
            request,
            current_user_id,
            int(request["buyer_id"]),
            request["buyer_name"],
        )
        return request

    @staticmethod
    def _serialize_favorite(row) -> Dict[str, Any]:
        """Convert a favorite row to template-friendly values."""

        favorite = dict(row)
        favorite["condition_label"] = favorite["condition"].title()
        favorite["status_label"] = favorite["status"].title()
        favorite["price_label"] = "{0:.2f}".format(favorite["price"])
        return favorite

    def _serialize_outgoing_request(self, row, current_user_id: int) -> Dict[str, Any]:
        """Convert a buyer request row to template-friendly values."""

        request = dict(row)
        request["listing_price_label"] = "{0:.2f}".format(request["listing_price"])
        request["status_label"] = request["status"].title()
        request["listing_status_label"] = request["listing_status"].title()
        self._attach_review_state(
            request,
            current_user_id,
            int(request["seller_id"]),
            request["seller_name"],
        )
        return request

    def _attach_review_state(
        self,
        request: Dict[str, Any],
        current_user_id: int,
        reviewed_user_id: int,
        reviewed_user_name: str,
    ) -> None:
        """Attach review form state for a request history card."""

        request["reviewed_user_id"] = reviewed_user_id
        request["reviewed_user_name"] = reviewed_user_name
        request["has_reviewed"] = self._review_exists(
            int(request["id"]),
            current_user_id,
            reviewed_user_id,
        )
        request["can_review"] = (
            request["status"] == REQUEST_STATUS_COMPLETED
            and not request["has_reviewed"]
        )

transaction_service = TransactionService()
