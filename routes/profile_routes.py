"""Profile routes."""

from flask import Blueprint, render_template
from utils.decorators import login_required

profile_bp = Blueprint("profiles", __name__)


@profile_bp.get("/profiles/<int:user_id>")
def view_public_profile(user_id: int) -> str:
    """Render the public profile page."""

    return render_template("profile.html", user_id=user_id)


@profile_bp.get("/profile/edit")
@login_required
def edit_profile_page() -> str:
    """Render the edit profile page."""

    return render_template("edit_profile.html")


@profile_bp.post("/profile/edit")
@login_required
def edit_profile() -> str:
    """Handle profile edit submission."""

    return "TODO: edit profile"
