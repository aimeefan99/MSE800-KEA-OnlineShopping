"""Transaction-related service logic for favorites, requests, and reviews."""

import sqlite3
from typing import Any, Dict, List, Mapping, Optional, Tuple

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
    users.preferred_contact_method AS buyer_contact_method,
    EXISTS (
        SELECT 1
        FROM reviews
        WHERE reviews.request_id = requests.id
            AND reviews.reviewer_id = requests.seller_id
            AND reviews.reviewed_user_id = requests.buyer_id
    ) AS has_review
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
    users.display_name AS seller_name,
    EXISTS (
        SELECT 1
        FROM reviews
        WHERE reviews.request_id = requests.id
            AND reviews.reviewer_id = requests.buyer_id
            AND reviews.reviewed_user_id = requests.seller_id
    ) AS has_review
FROM requests
INNER JOIN listings ON listings.id = requests.listing_id
INNER JOIN users ON users.id = requests.seller_id
WHERE requests.buyer_id = ?
ORDER BY requests.created_at DESC, requests.id DESC
"""
INSERT_REVIEW_SQL = """
INSERT INTO reviews (
    request_id,
    reviewer_id,
    reviewed_user_id,
    score,
    comment,
    created_at
)
VALUES (?, ?, ?, ?, ?, datetime('now'))
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
        return [self._serialize_incoming_request(request) for request in requests]

    def request_history(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get the current user's sent and received request views for the request hub."""

        db = get_db()
        outgoing_requests = db.execute(OUTGOING_REQUESTS_SQL, (user_id,)).fetchall()
        incoming_requests = db.execute(INCOMING_REQUESTS_SQL, (user_id,)).fetchall()
        return {
            "outgoing_requests": [
                self._serialize_outgoing_request(request) for request in outgoing_requests
            ],
            "incoming_requests": [
                self._serialize_incoming_request(request) for request in incoming_requests
            ],
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

        if request["status"] != REQUEST_STATUS_ACCEPTED:
            return False, "Only accepted requests can be completed."

        self._mark_request_completed(request_id, int(request["listing_id"]))
        return True, "Transaction completed successfully."

    def create_review(
        self,
        reviewer_id: int,
        form_data: Mapping[str, str],
    ) -> Tuple[bool, str]:
        """Create one review for the other party in a completed request."""

        review_data = self._clean_review_data(form_data)
        validation_error = self._validate_review_fields(review_data)
        if validation_error is not None:
            return False, validation_error

        request = self._get_request_for_action(review_data["request_id"])
        if request is None:
            return False, "Purchase request not found."

        request_error = self._validate_review_request(reviewer_id, request, review_data)
        if request_error is not None:
            return False, request_error

        return self._insert_review(reviewer_id, review_data)

    @classmethod
    def _clean_review_data(cls, form_data: Mapping[str, str]) -> Dict[str, Any]:
        """Normalize review form values."""

        return {
            "request_id": cls._read_positive_int(form_data.get("request_id")),
            "reviewed_user_id": cls._read_positive_int(form_data.get("reviewed_user_id")),
            "score": cls._read_positive_int(form_data.get("score")),
            "comment": form_data.get("comment", "").strip(),
        }

    @staticmethod
    def _validate_review_fields(review_data: Mapping[str, Any]) -> Optional[str]:
        """Check required review form values."""

        required_fields = ["request_id", "reviewed_user_id", "score"]
        if not all(review_data.get(field) is not None for field in required_fields):
            return "Please complete all required review fields."

        score = int(review_data["score"])
        if score < 1 or score > 5:
            return "Review score must be between 1 and 5."
        return None

    @staticmethod
    def _validate_review_request(
        reviewer_id: int,
        request,
        review_data: Mapping[str, Any],
    ) -> Optional[str]:
        """Check whether the completed request can be reviewed by this user."""

        if request["is_locked"]:
            return "This request is locked and cannot be reviewed."

        if request["status"] != REQUEST_STATUS_COMPLETED:
            return "Only completed transactions can be reviewed."

        expected_reviewed_user_id = TransactionService._get_reviewed_user_id(
            reviewer_id,
            request,
        )
        if expected_reviewed_user_id is None:
            return "You can only review transactions you participated in."

        if int(review_data["reviewed_user_id"]) != expected_reviewed_user_id:
            return "You can only review the other party in this transaction."
        return None

    @staticmethod
    def _get_reviewed_user_id(reviewer_id: int, request) -> Optional[int]:
        """Return the other party in the request for this reviewer."""

        buyer_id = int(request["buyer_id"])
        seller_id = int(request["seller_id"])
        if reviewer_id == buyer_id:
            return seller_id
        if reviewer_id == seller_id:
            return buyer_id
        return None

    @staticmethod
    def _insert_review(
        reviewer_id: int,
        review_data: Mapping[str, Any],
    ) -> Tuple[bool, str]:
        """Persist a validated review record."""

        db = get_db()
        try:
            insert_values = TransactionService._get_review_insert_values(
                reviewer_id,
                review_data,
            )
            db.execute(INSERT_REVIEW_SQL, insert_values)
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return False, "You have already reviewed this transaction."

        return True, "Review submitted successfully."

    @staticmethod
    def _get_review_insert_values(
        reviewer_id: int,
        review_data: Mapping[str, Any],
    ) -> Tuple[int, int, int, int, Optional[str]]:
        """Build database values for a review insert."""

        return (
            review_data["request_id"],
            reviewer_id,
            review_data["reviewed_user_id"],
            review_data["score"],
            review_data["comment"] or None,
        )

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
    def _read_positive_int(value: Optional[str]) -> Optional[int]:
        """Parse a form value into a positive integer."""

        try:
            parsed_value = int(value or "")
        except ValueError:
            return None
        if parsed_value <= 0:
            return None
        return parsed_value

    @staticmethod
    def _serialize_incoming_request(row) -> Dict[str, Any]:
        """Convert an incoming request row to template-friendly values."""

        request = dict(row)
        request["listing_price_label"] = "{0:.2f}".format(request["listing_price"])
        request["status_label"] = request["status"].title()
        request["listing_status_label"] = request["listing_status"].title()
        request["reviewed_user_id"] = request["buyer_id"]
        request["reviewed_user_name"] = request["buyer_name"]
        request["has_review"] = bool(request["has_review"])
        if request["buyer_contact_method"] == CONTACT_METHOD_PHONE:
            request["buyer_contact_method_label"] = "Phone"
            request["buyer_contact_value"] = request["buyer_phone_number"] or "Not provided"
        else:
            request["buyer_contact_method_label"] = "Email"
            request["buyer_contact_value"] = request["buyer_email"] or "Not provided"
        return request

    @staticmethod
    def _serialize_favorite(row) -> Dict[str, Any]:
        """Convert a favorite row to template-friendly values."""

        favorite = dict(row)
        favorite["condition_label"] = favorite["condition"].title()
        favorite["status_label"] = favorite["status"].title()
        favorite["price_label"] = "{0:.2f}".format(favorite["price"])
        return favorite

    @staticmethod
    def _serialize_outgoing_request(row) -> Dict[str, Any]:
        """Convert a buyer request row to template-friendly values."""

        request = dict(row)
        request["listing_price_label"] = "{0:.2f}".format(request["listing_price"])
        request["status_label"] = request["status"].title()
        request["listing_status_label"] = request["listing_status"].title()
        request["reviewed_user_id"] = request["seller_id"]
        request["reviewed_user_name"] = request["seller_name"]
        request["has_review"] = bool(request["has_review"])
        return request

transaction_service = TransactionService()
