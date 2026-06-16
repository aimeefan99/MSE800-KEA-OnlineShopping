"""Listing routes."""

from pathlib import Path

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, session, url_for

from services.listing_service import listing_service
from utils.decorators import login_required

listing_bp = Blueprint("listings", __name__)


@listing_bp.get("/listings")
def browse_listings() -> str:
    """Render the listing browse page."""

    listings = listing_service.browse_listings()
    return render_template(
        "listings.html",
        listings=_decorate_listing_images(listings),
    )


@listing_bp.get("/uploads/<path:filename>")
def uploaded_file(filename: str):
    """Serve uploaded listing images from the runtime upload directory."""

    normalized_filename = _strip_upload_prefix(filename)
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    image_path = upload_folder / normalized_filename
    if image_path.is_file():
        return send_from_directory(upload_folder, normalized_filename)

    legacy_upload_folder = Path(current_app.config["LEGACY_UPLOAD_FOLDER"])
    legacy_image_path = legacy_upload_folder / normalized_filename
    if legacy_image_path.is_file():
        return send_from_directory(legacy_upload_folder, normalized_filename)

    abort(404)


def _decorate_listing_images(listings):
    """Attach a resolved image source to each listing for template rendering."""

    for listing in listings:
        listing["image_src"] = _resolve_listing_image_url(listing["image_url"])
    return listings


def _resolve_listing_image_url(image_url: str) -> str:
    """Return the uploaded image URL or a stable placeholder when the file is missing."""

    normalized_filename = _strip_upload_prefix(image_url)
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    if (upload_folder / normalized_filename).is_file():
        return url_for("listings.uploaded_file", filename=image_url)

    legacy_upload_folder = Path(current_app.config["LEGACY_UPLOAD_FOLDER"])
    if (legacy_upload_folder / normalized_filename).is_file():
        return url_for("listings.uploaded_file", filename=image_url)

    return url_for("static", filename="images/listing-placeholder.svg")


def _strip_upload_prefix(value: str) -> str:
    """Normalize stored upload paths for Python 3.8 compatibility."""

    prefix = "uploads/"
    if value.startswith(prefix):
        return value[len(prefix):]
    return value


@listing_bp.get("/listings/<int:listing_id>")
def view_listing_detail(listing_id: int) -> str:
    """Render the listing detail page."""

    listing = listing_service.get_listing_detail(listing_id)
    if listing is None:
        abort(404)
    listing["image_src"] = _resolve_listing_image_url(listing["image_url"])
    return render_template("listing_detail.html", listing=listing)


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
