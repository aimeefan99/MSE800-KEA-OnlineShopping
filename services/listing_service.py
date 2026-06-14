"""Listing service placeholders."""

from services.base_service import BaseService


class ListingService(BaseService):
    """Handle listing-related business logic."""

    def create_listing(self) -> None:
        """Create a listing."""

        raise NotImplementedError

    def edit_listing(self) -> None:
        """Edit a listing."""

        raise NotImplementedError

    def delete_listing(self) -> None:
        """Delete a listing."""

        raise NotImplementedError

    def browse_listings(self) -> None:
        """Browse listings."""

        raise NotImplementedError

    def get_listing_detail(self) -> None:
        """Get listing detail."""

        raise NotImplementedError


listing_service = ListingService()
