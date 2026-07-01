"""Homepage recommendation routes."""

from flask import Blueprint, Response, jsonify, session

from services.recommendation_service import recommendation_service

recommendation_bp = Blueprint("recommendations", __name__)


@recommendation_bp.get("/recommendations/homepage")
def homepage_recommendations() -> Response:
    """Return homepage recommendation listing results."""

    recent_category_id = session.get("recent_interest_category_id")
    recommendations = recommendation_service.get_homepage_recommendations(
        recent_category_id
    )
    return jsonify(recommendations["listings"])
