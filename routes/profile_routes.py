"""Profile routes."""

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from services.profile_service import profile_service
from utils.decorators import login_required

profile_bp = Blueprint("profiles", __name__)


@profile_bp.get("/profiles/<int:user_id>")
def view_public_profile(user_id: int) -> str:
    """Render the public profile page."""

    profile_data = profile_service.get_public_profile(user_id)
    if profile_data is None:
        abort(404)
    return render_template("profile.html", profile=profile_data)


@profile_bp.get("/profile/edit")
@login_required
def edit_profile_page() -> str:
    """Render the edit profile page."""

    # Always load the form from the current session user.
    profile_data = profile_service.get_edit_profile_data(session["user_id"])
    if profile_data is None:
        flash("User not found.", "danger")
        return redirect(url_for("home"))

    return render_template("edit_profile.html", form_data=profile_data)


@profile_bp.post("/profile/edit")
@login_required
def edit_profile() -> str:
    """Handle profile edit submission."""

    # Keep validation and persistence in the service layer.
    success, error_message, form_data = profile_service.edit_profile(session["user_id"], request.form)
    if not success:
        flash(error_message, "danger")
        return render_template("edit_profile.html", form_data=form_data)

    # Keep the navbar display name aligned with the saved profile value.
    session["display_name"] = form_data["display_name"]
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profiles.edit_profile_page"))
