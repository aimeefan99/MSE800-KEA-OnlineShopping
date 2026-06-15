"""Authentication service placeholders."""

from datetime import date, datetime
from typing import Mapping, Optional, Tuple
import re

from werkzeug.security import generate_password_hash

from models.db import get_db
from services.base_service import BaseService


class AuthService(BaseService):
    """Handle authentication-related business logic."""

    def register_user(self, form_data: Mapping[str, str]) -> Tuple[bool, Optional[str]]:
        """Register a new user from form input."""

        display_name = form_data.get("display_name", "").strip()
        full_name = form_data.get("full_name", "").strip()
        date_of_birth = form_data.get("date_of_birth", "").strip()
        email = form_data.get("email", "").strip().lower()
        password = form_data.get("password", "")
        preferred_contact_method = form_data.get("preferred_contact_method", "").strip()
        phone_number = form_data.get("phone_number", "").strip()

        if not all(
            [display_name, full_name, date_of_birth, email, password, preferred_contact_method]
        ):
            return False, "Please complete all required fields."

        if preferred_contact_method not in {"email", "phone"}:
            return False, "Please select a valid contact method."

        if preferred_contact_method == "phone" and not phone_number:
            return False, "Phone number is required when phone is selected."

        password_error = self._validate_password(password)
        if password_error is not None:
            return False, password_error

        if not self._is_eligible_age(date_of_birth):
            return False, "You must be at least 18 years old to register."

        db = get_db()
        existing_user = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if existing_user is not None:
            return False, "This email is already registered."

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
                display_name,
                full_name,
                date_of_birth,
                email,
                phone_number or None,
                preferred_contact_method,
                generate_password_hash(password),
                datetime.utcnow().isoformat(),
            ),
        )
        db.commit()
        return True, None

    def login_user(self) -> None:
        """Log in a user."""

        raise NotImplementedError

    def logout_user(self) -> None:
        """Log out a user."""

        raise NotImplementedError

    @staticmethod
    def _is_eligible_age(date_of_birth: str) -> bool:
        """Check whether the user is at least 18 years old."""

        try:
            birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            return False

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
