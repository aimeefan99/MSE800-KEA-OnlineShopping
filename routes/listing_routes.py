"""Listing routes."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.listing_service import listing_service
from utils.decorators import login_required

listing_bp = Blueprint("listings", __name__)


@listing_bp.get("/listings")
def browse_listings() -> str:
    """Render the listing browse page."""

    return render_template("listings.html")


@listing_bp.get("/listings/<int:listing_id>")
def view_listing_detail(listing_id: int) -> str:
    """Render the listing detail page."""

    return render_template("listing_detail.html", listing_id=listing_id)


@listing_bp.get("/listings/create")
@login_required
def create_listing_page() -> str:
    """Render the create listing page."""

    return render_template(
        "create_listing.html",
        form_data={},
        categories=listing_service.get_category_options(),
        condition_options=listing_service.get_condition_options(),
    )


@listing_bp.post("/listings/create")
@login_required
def create_listing() -> str:
    """Handle listing creation."""

    # Keep form validation and persistence in the service layer.
    success, error_message, form_data, listing_id = listing_service.create_listing(
        session["user_id"],
        request.form,
        request.files.get("image"),
    )
    if not success:
        flash(error_message, "danger")
        return render_template(
            "create_listing.html",
            form_data=form_data,
            categories=listing_service.get_category_options(),
            condition_options=listing_service.get_condition_options(),
        )

    flash("Listing created successfully.", "success")
    return redirect(url_for("listings.view_listing_detail", listing_id=listing_id))


@listing_bp.get("/listings/<int:listing_id>/edit")
@login_required
def edit_listing_page(listing_id: int) -> str:
    """Render the edit listing page."""

    return render_template("edit_listing.html", listing_id=listing_id)


@listing_bp.post("/listings/<int:listing_id>/edit")
@login_required
def edit_listing(listing_id: int) -> str:
    """Handle listing edit."""

    return f"TODO: edit listing {listing_id}"


@listing_bp.post("/listings/<int:listing_id>/delete")
@login_required
def delete_listing(listing_id: int) -> str:
    """Handle listing deletion."""

    return f"TODO: delete listing {listing_id}"
