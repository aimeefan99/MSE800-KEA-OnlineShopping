"""Transaction-related service placeholders for favorites, requests, and reviews."""

from services.base_service import BaseService


class TransactionService(BaseService):
    """Handle favorites, requests, and review workflow logic."""

    def view_favorites(self) -> None:
        """Get favorite listings for the current user."""

        raise NotImplementedError

    def add_favorite(self) -> None:
        """Add a listing to the favorite list."""

        raise NotImplementedError

    def remove_favorite(self) -> None:
        """Remove a listing from the favorite list."""

        raise NotImplementedError

    def create_request(self) -> None:
        """Create a purchase request."""

        raise NotImplementedError

    def incoming_requests(self) -> None:
        """Get incoming requests for a seller."""

        raise NotImplementedError

    def request_history(self) -> None:
        """Get request history for a user."""

        raise NotImplementedError

    def accept_request(self) -> None:
        """Accept a purchase request."""

        raise NotImplementedError

    def reject_request(self) -> None:
        """Reject a purchase request."""

        raise NotImplementedError

    def complete_request(self) -> None:
        """Complete a purchase request."""

        raise NotImplementedError

    def create_review(self) -> None:
        """Create a review."""

        raise NotImplementedError

transaction_service = TransactionService()
