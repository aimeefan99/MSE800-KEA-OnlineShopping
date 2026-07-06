"""Profile routes."""

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from services.listing_service import listing_service
from services.profile_service import profile_service
from utils.decorators import marketplace_user_required
from utils.listing_images import attach_listing_image_sources

profile_bp = Blueprint("profiles", __name__)


@profile_bp.get("/profiles/<int:user_id>")
def view_public_profile(user_id: int) -> str:
    """Render the public profile page."""

    profile_data = profile_service.get_public_profile(user_id)
    if profile_data is None:
        abort(404)
    return render_template("profile.html", profile=profile_data)


@profile_bp.get("/profile/edit")
@marketplace_user_required
def edit_profile_page() -> str:
    """Keep the legacy profile edit route pointing to the account area."""

    return redirect(url_for("profiles.account_page"))


@profile_bp.get("/account")
@marketplace_user_required
def account_page() -> str:
    """Render the account profile section."""

    profile_data = profile_service.get_edit_profile_data(session["user_id"])
    if profile_data is None:
        flash("User not found.", "danger")
        return redirect(url_for("home"))

    return render_template(
        "edit_profile.html",
        form_data=profile_data,
        active_account_section="profile",
    )


@profile_bp.get("/account/listings")
@marketplace_user_required
def account_listings_page() -> str:
    """Render the current user's listing management page."""

    listings = listing_service.get_user_listings(session["user_id"])
    return render_template(
        "account_listings.html",
        listings=attach_listing_image_sources(listings),
        active_account_section="listings",
    )


@profile_bp.post("/profile/edit")
@marketplace_user_required
def edit_profile() -> str:
    """Handle profile edit submission."""

    # Keep validation and persistence in the service layer.
    success, error_message, form_data = profile_service.edit_profile(session["user_id"], request.form)
    if not success:
        flash(error_message, "danger")
        return render_template(
            "edit_profile.html",
            form_data=form_data,
            active_account_section="profile",
        )

    # Keep the navbar display name aligned with the saved profile value.
    session["display_name"] = form_data["display_name"]
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profiles.account_page"))
