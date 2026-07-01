"""Profile service logic."""

from typing import Any, Dict, Mapping, Optional, Tuple

from models.db import get_db
from services.base_service import BaseService
from utils.constants import (
    CONTACT_METHOD_PHONE,
    LISTING_STATUS_AVAILABLE,
    LISTING_STATUS_SOLD,
    REQUEST_STATUS_COMPLETED,
)


class ProfileService(BaseService):
    """Handle profile-related business logic."""

    def get_public_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get public profile data."""

        db = get_db()
        profile = db.execute(
            """
            SELECT
                users.id,
                users.display_name,
                users.bio,
                users.preferred_contact_method,
                users.email,
                users.phone_number,
                users.created_at,
                COUNT(CASE WHEN listings.status = ? THEN 1 END) AS active_listing_count,
                COUNT(CASE WHEN listings.status = ? THEN 1 END) AS sold_listing_count
            FROM users
            LEFT JOIN listings ON listings.seller_id = users.id
            WHERE users.id = ?
            GROUP BY
                users.id,
                users.display_name,
                users.bio,
                users.preferred_contact_method,
                users.email,
                users.phone_number,
                users.created_at
            """,
            (LISTING_STATUS_AVAILABLE, LISTING_STATUS_SOLD, user_id),
        ).fetchone()
        if profile is None:
            return None

        profile_data = self._serialize_public_profile(profile)
        self._attach_review_summary(profile_data, user_id)
        self._attach_completed_transaction_count(profile_data, user_id)
        return profile_data

    def get_edit_profile_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get editable profile data for the current user."""

        user = self._get_user_by_id(user_id)
        if user is None:
            return None
        return dict(user)

    def edit_profile(
        self, user_id: int, form_data: Mapping[str, str]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Update the editable fields for the current user."""

        # Return cleaned form data on failure so the form can be re-rendered.
        cleaned_data = self._clean_profile_data(form_data)
        validation_error = self._validate_profile_data(cleaned_data)
        if validation_error is not None:
            return False, validation_error, cleaned_data

        if self._get_user_by_id(user_id) is None:
            return False, "User not found.", cleaned_data

        self._update_profile(user_id, cleaned_data)
        return True, None, cleaned_data

    @staticmethod
    def _clean_profile_data(form_data: Mapping[str, str]) -> Dict[str, str]:
        """Normalize editable profile values."""

        return {
            "display_name": form_data.get("display_name", "").strip(),
            "full_name": form_data.get("full_name", "").strip(),
            "phone_number": form_data.get("phone_number", "").strip(),
            "preferred_contact_method": form_data.get("preferred_contact_method", "").strip(),
            "bio": form_data.get("bio", "").strip(),
        }

    def _validate_profile_data(self, cleaned_data: Mapping[str, str]) -> Optional[str]:
        """Check profile update rules."""

        required_fields = ["display_name", "full_name", "preferred_contact_method"]
        if not all(cleaned_data[field] for field in required_fields):
            return "Please complete all required fields."

        # Profile updates keep the same contact-method rule used at registration.
        preferred_contact_method = cleaned_data["preferred_contact_method"]
        if preferred_contact_method not in {"email", CONTACT_METHOD_PHONE}:
            return "Please select a valid contact method."

        if preferred_contact_method == CONTACT_METHOD_PHONE and not cleaned_data["phone_number"]:
            return "Phone number is required when phone is selected."
        return None

    @staticmethod
    def _get_user_by_id(user_id: int) -> Any:
        """Fetch a user by id."""

        db = get_db()
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    @staticmethod
    def _update_profile(user_id: int, cleaned_data: Mapping[str, str]) -> None:
        """Save profile changes for the current user."""

        db = get_db()
        db.execute(
            """
            UPDATE users
            SET display_name = ?,
                full_name = ?,
                phone_number = ?,
                preferred_contact_method = ?,
                bio = ?
            WHERE id = ?
            """,
            (
                cleaned_data["display_name"],
                cleaned_data["full_name"],
                cleaned_data["phone_number"] or None,
                cleaned_data["preferred_contact_method"],
                cleaned_data["bio"] or None,
                user_id,
            ),
        )
        db.commit()

    @staticmethod
    def _serialize_public_profile(row) -> Dict[str, Any]:
        """Convert public profile data to template-friendly values."""

        profile = dict(row)
        profile["bio"] = profile.get("bio") or "No public bio provided yet."
        profile["member_since_label"] = str(profile["created_at"])[:10]
        if profile["preferred_contact_method"] == CONTACT_METHOD_PHONE:
            profile["preferred_contact_method_label"] = "Phone"
            profile["public_contact_value"] = profile.get("phone_number") or "Not provided"
        else:
            profile["preferred_contact_method_label"] = "Email"
            profile["public_contact_value"] = profile.get("email") or "Not provided"
        return profile

    @staticmethod
    def _attach_review_summary(profile: Dict[str, Any], user_id: int) -> None:
        """Attach public trust indicators from completed transaction reviews."""

        db = get_db()
        summary = db.execute(
            """
            SELECT COUNT(*) AS review_count, AVG(score) AS average_score
            FROM reviews
            WHERE reviewed_user_id = ?
            """,
            (user_id,),
        ).fetchone()
        reviews = db.execute(
            """
            SELECT
                reviews.score,
                reviews.comment,
                reviews.created_at,
                users.display_name AS reviewer_name
            FROM reviews
            INNER JOIN users ON users.id = reviews.reviewer_id
            WHERE reviews.reviewed_user_id = ?
            ORDER BY reviews.created_at DESC, reviews.id DESC
            LIMIT 3
            """,
            (user_id,),
        ).fetchall()

        profile["review_count"] = int(summary["review_count"])
        average_score = summary["average_score"]
        profile["average_score_label"] = (
            "{0:.1f}".format(average_score) if average_score is not None else "No ratings yet"
        )
        profile["recent_reviews"] = [dict(review) for review in reviews]

    @staticmethod
    def _attach_completed_transaction_count(profile: Dict[str, Any], user_id: int) -> None:
        """Attach completed request count where the user was buyer or seller."""

        db = get_db()
        result = db.execute(
            """
            SELECT COUNT(*) AS completed_transaction_count
            FROM requests
            WHERE status = ?
                AND (buyer_id = ? OR seller_id = ?)
            """,
            (REQUEST_STATUS_COMPLETED, user_id, user_id),
        ).fetchone()
        profile["completed_transaction_count"] = int(
            result["completed_transaction_count"]
        )


profile_service = ProfileService()
