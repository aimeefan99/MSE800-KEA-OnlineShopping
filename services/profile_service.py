"""Profile service logic."""

from typing import Any, Dict, Mapping, Optional, Tuple

from models.db import get_db
from services.base_service import BaseService


class ProfileService(BaseService):
    """Handle profile-related business logic."""

    def get_public_profile(self) -> None:
        """Get public profile data."""

        raise NotImplementedError

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
        if preferred_contact_method not in {"email", "phone"}:
            return "Please select a valid contact method."

        if preferred_contact_method == "phone" and not cleaned_data["phone_number"]:
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


profile_service = ProfileService()
