"""AI listing routes."""

from flask import Blueprint, render_template

ai_bp = Blueprint("ai", __name__)


@ai_bp.get("/ai/listing")
def ai_listing_page() -> str:
    """Render the AI listing page."""

    return render_template("ai_listing.html")


@ai_bp.post("/ai/listing-draft")
def generate_listing_draft() -> str:
    """Handle AI listing draft generation."""

    return "TODO: generate AI listing draft"
