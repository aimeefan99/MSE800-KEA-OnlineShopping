"""Authentication service placeholders."""

from services.base_service import BaseService


class AuthService(BaseService):
    """Handle authentication-related business logic."""

    def register_user(self) -> None:
        """Register a new user."""

        raise NotImplementedError

    def login_user(self) -> None:
        """Log in a user."""

        raise NotImplementedError

    def logout_user(self) -> None:
        """Log out a user."""

        raise NotImplementedError


auth_service = AuthService()
