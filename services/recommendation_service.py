"""Recommendation service logic for personalized marketplace discovery."""

from typing import Any, Dict, List, Optional

from models.db import get_db
from services.base_service import BaseService
from services.listing_service import ListingService
from utils.constants import LISTING_STATUS_AVAILABLE

HOMEPAGE_RECOMMENDATION_LIMIT = 6
HOMEPAGE_LISTINGS_SQL = """
SELECT
    listings.id,
    listings.seller_id,
    listings.title,
    listings.description,
    listings.condition,
    listings.price,
    listings.image_url,
    listings.status,
    listings.created_at,
    categories.name AS category_name,
    users.display_name AS seller_name
FROM listings
INNER JOIN categories ON categories.id = listings.category_id
INNER JOIN users ON users.id = listings.seller_id
WHERE listings.status = ?
    AND {extra_where_clause}
ORDER BY listings.created_at DESC, listings.id DESC
LIMIT ?
"""


class RecommendationService(BaseService):
    """Handle homepage recommendation logic."""

    def get_homepage_recommendations(
        self,
        recent_category_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get homepage recommendations from the user's recent category interest."""

        category = self._get_category(recent_category_id)
        if category is not None:
            listings = self._get_listings_for_category(category["id"])
            if listings:
                return {
                    "interest_category": category,
                    "listings": listings,
                    "is_personalized": True,
                }

        return {
            "interest_category": None,
            "listings": self._get_recent_available_listings(),
            "is_personalized": False,
        }

    @staticmethod
    def _get_category(category_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """Return a category if the recent interest id is valid."""

        if category_id is None:
            return None

        db = get_db()
        category = db.execute(
            "SELECT id, name FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
        if category is None:
            return None
        return dict(category)

    def _get_listings_for_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Return available listings in the user's recent interest category."""

        return self._get_available_listings("listings.category_id = ?", [category_id])

    def _get_recent_available_listings(self) -> List[Dict[str, Any]]:
        """Return recent available listings when there is no useful interest signal."""

        return self._get_available_listings("1 = 1", [])

    @staticmethod
    def _get_available_listings(
        extra_where_clause: str,
        extra_parameters: List[Any],
    ) -> List[Dict[str, Any]]:
        """Return available listing cards for the homepage."""

        db = get_db()
        query_parameters = (
            [LISTING_STATUS_AVAILABLE]
            + extra_parameters
            + [HOMEPAGE_RECOMMENDATION_LIMIT]
        )
        listings = db.execute(
            HOMEPAGE_LISTINGS_SQL.format(extra_where_clause=extra_where_clause),
            query_parameters,
        ).fetchall()
        return [ListingService._serialize_listing_row(listing) for listing in listings]


recommendation_service = RecommendationService()
