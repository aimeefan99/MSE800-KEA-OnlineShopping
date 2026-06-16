"""Recommendation service placeholders."""

from services.base_service import BaseService


class RecommendationService(BaseService):
    """Handle homepage recommendation logic."""

    def get_homepage_recommendations(self) -> None:
        """Get homepage recommendations."""

        raise NotImplementedError


recommendation_service = RecommendationService()
