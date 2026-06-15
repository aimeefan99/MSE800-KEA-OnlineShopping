"""Authentication service logic."""

from datetime import date, datetime
import re
from typing import Any, Dict, Mapping, Optional, Tuple

from werkzeug.security import check_password_hash, generate_password_hash

from models.db import get_db
from services.base_service import BaseService


class AuthService(BaseService):
    """Handle authentication-related business logic."""

    def register_user(self, form_data: Mapping[str, str]) -> Tuple[bool, Optional[str]]:
        """Register a new user from validated form input."""

        cleaned_data = self._clean_registration_data(form_data)
        validation_error = self._validate_registration_data(cleaned_data)
        if validation_error is not None:
            return False, validation_error

        if self._email_exists(cleaned_data["email"]):
            return False, "This email is already registered."

        self._create_user(cleaned_data)
        return True, None

    def login_user(self, form_data: Mapping[str, str]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Validate login credentials and return the matching user."""

        email = form_data.get("email", "").strip().lower()
        password = form_data.get("password", "")
        if not email or not password:
            return None, "Please enter your email and password."

        user = self._get_user_by_email(email)
        # Passwords are stored as hashes, so login must verify the hash instead of plain text.
        if user is None or not check_password_hash(user["password_hash"], password):
            return None, "Invalid email or password."

        if user["is_locked"]:
            return None, "This account is locked."

        return dict(user), None

    @staticmethod
    def build_session_data(user: Mapping[str, Any]) -> Dict[str, Any]:
        """Build the stored session values for a logged-in user."""

        return {
            "user_id": user["id"],
            "display_name": user["display_name"],
            "role": user["role"],
        }

    def _clean_registration_data(self, form_data: Mapping[str, str]) -> Dict[str, str]:
        """Normalize registration input values."""

        return {
            "display_name": form_data.get("display_name", "").strip(),
            "full_name": form_data.get("full_name", "").strip(),
            "date_of_birth": form_data.get("date_of_birth", "").strip(),
            "email": form_data.get("email", "").strip().lower(),
            "password": form_data.get("password", ""),
            "preferred_contact_method": form_data.get("preferred_contact_method", "").strip(),
            "phone_number": form_data.get("phone_number", "").strip(),
        }

    def _validate_registration_data(self, cleaned_data: Mapping[str, str]) -> Optional[str]:
        """Check registration rules before user creation."""

        required_fields = [
            "display_name",
            "full_name",
            "date_of_birth",
            "email",
            "password",
            "preferred_contact_method",
        ]
        if not all(cleaned_data[field] for field in required_fields):
            return "Please complete all required fields."

        contact_error = self._validate_contact_method(cleaned_data)
        if contact_error is not None:
            return contact_error

        password_error = self._validate_password(cleaned_data["password"])
        if password_error is not None:
            return password_error

        if not self._is_eligible_age(cleaned_data["date_of_birth"]):
            return "You must be at least 18 years old to register."
        return None

    @staticmethod
    def _validate_contact_method(cleaned_data: Mapping[str, str]) -> Optional[str]:
        """Check contact method and related contact detail rules."""

        preferred_contact_method = cleaned_data["preferred_contact_method"]
        if preferred_contact_method not in {"email", "phone"}:
            return "Please select a valid contact method."

        if preferred_contact_method == "phone" and not cleaned_data["phone_number"]:
            return "Phone number is required when phone is selected."
        return None

    def _email_exists(self, email: str) -> bool:
        """Check whether an email is already registered."""

        return self._get_user_by_email(email) is not None

    @staticmethod
    def _get_user_by_email(email: str) -> Any:
        """Fetch a user record by email."""

        db = get_db()
        return db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    def _create_user(self, cleaned_data: Mapping[str, str]) -> None:
        """Insert a validated user record."""

        db = get_db()
        # Store the new user only after all validation rules have passed.
        db.execute(
            """
            INSERT INTO users (
                display_name,
                full_name,
                date_of_birth,
                email,
                phone_number,
                preferred_contact_method,
                password_hash,
                role,
                is_locked,
                bio,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'user', 0, NULL, ?)
            """,
            (
                cleaned_data["display_name"],
                cleaned_data["full_name"],
                cleaned_data["date_of_birth"],
                cleaned_data["email"],
                cleaned_data["phone_number"] or None,
                cleaned_data["preferred_contact_method"],
                generate_password_hash(cleaned_data["password"]),
                datetime.utcnow().isoformat(),
            ),
        )
        db.commit()

    @staticmethod
    def _is_eligible_age(date_of_birth: str) -> bool:
        """Check whether the user is at least 18 years old."""

        try:
            birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            return False

        # Age is calculated against today's date so underage registration is blocked.
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age >= 18

    @staticmethod
    def _validate_password(password: str) -> Optional[str]:
        """Validate password strength against project rules."""

        if len(password) < 6:
            return "Password must be at least 6 characters long."
        if not re.search(r"[A-Z]", password):
            return "Password must include at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return "Password must include at least one lowercase letter."
        if not re.search(r"\d", password):
            return "Password must include at least one number."
        return None


auth_service = AuthService()
