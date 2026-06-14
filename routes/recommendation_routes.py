"""Homepage recommendation routes."""

from flask import Blueprint

recommendation_bp = Blueprint("recommendations", __name__)


@recommendation_bp.get("/recommendations/homepage")
def homepage_recommendations() -> str:
    """Return homepage recommendation placeholder."""

    return "TODO: homepage recommendations"
