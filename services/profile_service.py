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
        public_profile = self._serialize_public_profile(profile)
        public_profile.update(self._get_trust_summary(user_id))
        return public_profile

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
    def _get_trust_summary(user_id: int) -> Dict[str, Any]:
        """Return public trust indicators for a profile."""

        review_stats = ProfileService._get_review_stats(user_id)
        recent_reviews = ProfileService._get_recent_reviews(user_id)
        return ProfileService._serialize_trust_summary(
            ProfileService._count_completed_transactions(user_id),
            review_stats,
            recent_reviews,
        )

    @staticmethod
    def _count_completed_transactions(user_id: int) -> int:
        """Count completed requests where the user was buyer or seller."""

        db = get_db()
        count_row = db.execute(
            """
            SELECT COUNT(*) AS transaction_count
            FROM requests
            WHERE status = ?
                AND (buyer_id = ? OR seller_id = ?)
            """,
            (REQUEST_STATUS_COMPLETED, user_id, user_id),
        ).fetchone()
        return int(count_row["transaction_count"] or 0)

    @staticmethod
    def _get_review_stats(user_id: int):
        """Fetch rating and positive feedback totals for a user."""

        db = get_db()
        return db.execute(
            """
            SELECT
                COUNT(*) AS review_count,
                AVG(score) AS average_rating,
                SUM(CASE WHEN score >= 4 THEN 1 ELSE 0 END) AS positive_review_count
            FROM reviews
            WHERE reviewed_user_id = ?
            """,
            (user_id,),
        ).fetchone()

    @staticmethod
    def _get_recent_reviews(user_id: int):
        """Fetch the newest public reviews for a user."""

        db = get_db()
        return db.execute(
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

    @staticmethod
    def _serialize_trust_summary(
        completed_transaction_count: int,
        review_stats,
        recent_reviews,
    ) -> Dict[str, Any]:
        """Convert trust query results into template-friendly values."""

        review_count = int(review_stats["review_count"] or 0)
        average_rating = review_stats["average_rating"]
        positive_rate = ProfileService._calculate_positive_feedback_rate(
            review_count,
            review_stats["positive_review_count"],
        )
        return {
            "completed_transaction_count": completed_transaction_count,
            "review_count": review_count,
            "average_rating_label": (
                "{0:.1f} / 5".format(float(average_rating))
                if average_rating is not None
                else "No ratings yet"
            ),
            "positive_feedback_label": (
                "{0}% positive".format(positive_rate)
                if positive_rate is not None
                else "No feedback yet"
            ),
            "recent_reviews": [dict(review) for review in recent_reviews],
        }

    @staticmethod
    def _calculate_positive_feedback_rate(
        review_count: int,
        positive_review_count,
    ) -> Optional[int]:
        """Calculate the percentage of reviews scored four or higher."""

        if review_count == 0:
            return None
        return round((int(positive_review_count or 0) / review_count) * 100)


profile_service = ProfileService()
