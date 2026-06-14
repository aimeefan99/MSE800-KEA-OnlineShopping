"""Profile service placeholders."""

from services.base_service import BaseService


class ProfileService(BaseService):
    """Handle profile-related business logic."""

    def get_public_profile(self) -> None:
        """Get public profile data."""

        raise NotImplementedError

    def edit_profile(self) -> None:
        """Edit a user profile."""

        raise NotImplementedError


profile_service = ProfileService()
