"""AI listing service placeholders."""

from services.base_service import BaseService


class AIListingService(BaseService):
    """Handle AI-assisted listing generation."""

    def generate_ai_listing_draft(self) -> None:
        """Generate an AI listing draft."""

        raise NotImplementedError


ai_listing_service = AIListingService()
