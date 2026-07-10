"""AI listing routes."""

from flask import Blueprint, jsonify, render_template, request

from services.ai_service import ai_listing_service
from utils.decorators import marketplace_user_required

ai_bp = Blueprint("ai", __name__)


@ai_bp.get("/ai/listing")
def ai_listing_page() -> str:
    """Render the AI listing page."""

    return render_template("ai_listing.html")


@ai_bp.post("/ai/listing-draft")
@marketplace_user_required
def generate_listing_draft() -> str:
    """Handle AI listing draft generation."""
    success, error_message, draft = ai_listing_service.generate_listing_draft(
        request.files.get("image")
    )
    if not success:
        return jsonify({"success": False, "error": error_message}), 400
    return jsonify({"success": True, "draft": draft})
