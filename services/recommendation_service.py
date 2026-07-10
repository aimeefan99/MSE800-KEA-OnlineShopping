"""Recommendation service logic for lightweight homepage discovery."""

from typing import Any, Dict, List, Optional, Sequence

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
WHERE {where_clause}
ORDER BY listings.created_at DESC, listings.id DESC
LIMIT ?
"""


class RecommendationService(BaseService):
    """Handle homepage recommendation logic."""

    def get_homepage_recommendations(
        self,
        recent_category_ids: Optional[Sequence[int]] = None,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return useful homepage listings from recent and saved category signals."""

        interest_category_ids = self._get_interest_category_ids(
            recent_category_ids or [],
            user_id,
        )
        listings = self._get_ranked_available_listings(interest_category_ids, user_id)

        return {
            "interest_categories": self._get_category_names(interest_category_ids),
            "is_personalized": bool(interest_category_ids),
            "listings": listings,
        }

    def _get_interest_category_ids(
        self,
        recent_category_ids: Sequence[int],
        user_id: Optional[int],
    ) -> List[int]:
        """Combine recent browsing and favorite categories without duplicates."""

        interest_category_ids: List[int] = []
        for category_id in recent_category_ids:
            self._append_unique_category(interest_category_ids, category_id)

        if user_id is not None:
            for category_id in self._get_favorite_category_ids(user_id):
                self._append_unique_category(interest_category_ids, category_id)
        return interest_category_ids

    @staticmethod
    def _append_unique_category(category_ids: List[int], category_id: int) -> None:
        """Append a positive category id once."""

        if category_id > 0 and category_id not in category_ids:
            category_ids.append(category_id)

    @staticmethod
    def _get_favorite_category_ids(user_id: int) -> List[int]:
        """Return categories the user has saved in favorites, newest first."""

        db = get_db()
        categories = db.execute(
            """
            SELECT DISTINCT listings.category_id
            FROM favorite_list
            INNER JOIN listings ON listings.id = favorite_list.listing_id
            WHERE favorite_list.user_id = ?
            ORDER BY favorite_list.created_at DESC, favorite_list.id DESC
            """,
            (user_id,),
        ).fetchall()
        return [int(category["category_id"]) for category in categories]

    def _get_ranked_available_listings(
        self,
        interest_category_ids: Sequence[int],
        user_id: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Return matching listings first, then recent listings as fallback."""

        matching_listings = self._get_matching_interest_listings(
            interest_category_ids,
            user_id,
        )
        if len(matching_listings) >= HOMEPAGE_RECOMMENDATION_LIMIT:
            return matching_listings

        recent_listings = self._get_recent_available_listings(
            user_id,
            [listing["id"] for listing in matching_listings],
        )
        return (matching_listings + recent_listings)[:HOMEPAGE_RECOMMENDATION_LIMIT]

    def _get_matching_interest_listings(
        self,
        interest_category_ids: Sequence[int],
        user_id: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Return available listings grouped by interest recency."""

        matching_listings: List[Dict[str, Any]] = []
        for category_id in interest_category_ids:
            category_listings = self._get_available_listings(
                "listings.category_id = ?",
                [category_id],
                user_id,
                [listing["id"] for listing in matching_listings],
            )
            matching_listings.extend(category_listings)
            if len(matching_listings) >= HOMEPAGE_RECOMMENDATION_LIMIT:
                break
        return matching_listings[:HOMEPAGE_RECOMMENDATION_LIMIT]

    def _get_recent_available_listings(
        self,
        user_id: Optional[int],
        excluded_listing_ids: Sequence[int],
    ) -> List[Dict[str, Any]]:
        """Return recent available listings for fallback discovery."""

        return self._get_available_listings("1 = 1", [], user_id, excluded_listing_ids)

    @staticmethod
    def _get_available_listings(
        extra_where_clause: str,
        extra_parameters: List[Any],
        user_id: Optional[int],
        excluded_listing_ids: Sequence[int],
    ) -> List[Dict[str, Any]]:
        """Return available listing cards for homepage recommendations."""

        where_clause, parameters = RecommendationService._build_listing_query_parts(
            extra_where_clause,
            extra_parameters,
            user_id,
            excluded_listing_ids,
        )
        listings = get_db().execute(
            HOMEPAGE_LISTINGS_SQL.format(where_clause=where_clause),
            parameters,
        ).fetchall()
        return [ListingService._serialize_listing_row(listing) for listing in listings]

    @staticmethod
    def _build_listing_query_parts(
        extra_where_clause: str,
        extra_parameters: List[Any],
        user_id: Optional[int],
        excluded_listing_ids: Sequence[int],
    ) -> tuple:
        """Build homepage listing filters and query parameters."""

        where_clauses = ["listings.status = ?", extra_where_clause]
        parameters: List[Any] = [LISTING_STATUS_AVAILABLE] + extra_parameters

        if user_id is not None:
            where_clauses.append("listings.seller_id != ?")
            parameters.append(user_id)

        if excluded_listing_ids:
            placeholders = ", ".join("?" for _ in excluded_listing_ids)
            where_clauses.append("listings.id NOT IN ({0})".format(placeholders))
            parameters.extend(excluded_listing_ids)

        parameters.append(HOMEPAGE_RECOMMENDATION_LIMIT)
        return " AND ".join(where_clauses), parameters

    @staticmethod
    def _get_category_names(category_ids: Sequence[int]) -> List[str]:
        """Return display names for recommendation interest categories."""

        if not category_ids:
            return []

        placeholders = ", ".join("?" for _ in category_ids)
        categories = get_db().execute(
            """
            SELECT id, name
            FROM categories
            WHERE id IN ({0})
            """.format(placeholders),
            list(category_ids),
        ).fetchall()
        category_names = {
            int(category["id"]): str(category["name"])
            for category in categories
        }
        return [
            category_names[category_id]
            for category_id in category_ids
            if category_id in category_names
        ]


recommendation_service = RecommendationService()
