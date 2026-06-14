"""Factory classes for building domain objects."""

from models.entities import Listing, Request


class ListingFactory:
    """Create listing objects from different input sources."""

    @staticmethod
    def create_from_form(
        seller_id: int,
        category_id: int,
        title: str,
        description: str,
        condition: str,
        price: float,
        image_url: str,
    ) -> Listing:
        """Create a listing from standard user form input."""

        return Listing(
            seller_id=seller_id,
            category_id=category_id,
            title=title,
            description=description,
            condition=condition,
            price=price,
            image_url=image_url,
        )

    @staticmethod
    def create_from_ai_draft(
        seller_id: int,
        category_id: int,
        draft_title: str,
        draft_description: str,
        condition: str,
        price: float,
        image_url: str,
    ) -> Listing:
        """Create a listing from AI-assisted draft data."""

        return Listing(
            seller_id=seller_id,
            category_id=category_id,
            title=draft_title,
            description=draft_description,
            condition=condition,
            price=price,
            image_url=image_url,
        )


class RequestFactory:
    """Create request objects for the marketplace workflow."""

    @staticmethod
    def create_request(
        listing_id: int,
        buyer_id: int,
        seller_id: int,
        message: str = "",
    ) -> Request:
        """Create a pending purchase request."""

        return Request(
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            status="pending",
            message=message or None,
        )
