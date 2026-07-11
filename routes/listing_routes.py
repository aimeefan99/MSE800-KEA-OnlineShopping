"""Listing controller routes for creating, showing, editing, and deleting items."""

from pathlib import Path
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from services.listing_service import listing_service
from services.transaction_service import transaction_service
from utils.decorators import login_required, marketplace_user_required
from utils.listing_images import (
    attach_listing_image_sources,
    resolve_listing_image_url,
    strip_upload_prefix,
)

listing_bp = Blueprint("listings", __name__)
RECENT_INTEREST_LIMIT = 3


@listing_bp.get("/listings")
def browse_listings() -> str:
    """Render the listing browse page."""
    filters = {
        "keyword": request.args.get("keyword", "").strip(),
        "category_id": request.args.get("category_id", "").strip(),
        "condition": request.args.get("condition", "").strip(),
        "min_price": request.args.get("min_price", "").strip(),
        "max_price": request.args.get("max_price", "").strip(),
    }
    listings = listing_service.browse_listings(filters)
    if filters["category_id"].isdigit():
        _remember_interest_category(int(filters["category_id"]))
    elif filters["keyword"]:
        _remember_search_interest_categories(filters["keyword"], listings)

    return render_template(
        "listings.html",
        listings=attach_listing_image_sources(listings),
        filters=filters,
        categories=listing_service.get_category_options(),
        condition_options=listing_service.get_condition_options(),
    )


@listing_bp.get("/uploads/<path:filename>")
def uploaded_file(filename: str):
    """Serve uploaded listing images from the runtime upload directory."""
    normalized_filename = strip_upload_prefix(filename)
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    image_path = upload_folder / normalized_filename
    if image_path.is_file():
        return send_from_directory(upload_folder, normalized_filename)

    abort(404)


@listing_bp.get("/listings/<int:listing_id>")
def view_listing_detail(listing_id: int) -> str:
    """Render the listing detail page."""
    listing = listing_service.get_listing_detail(listing_id)
    if listing is None:
        abort(404)
    _remember_interest_category(int(listing["category_id"]))
    listing["image_src"] = resolve_listing_image_url(listing["image_url"])
    favorite_id = None
    request_status = None
    if "user_id" in session:
        favorite_id = transaction_service.get_favorite_id(session["user_id"], listing_id)
        request_status = transaction_service.get_request_status(session["user_id"], listing_id)
    return render_template(
        "listing_detail.html",
        listing=listing,
        favorite_id=favorite_id,
        request_status=request_status,
    )


@listing_bp.get("/listings/create")
@marketplace_user_required
def create_listing_page() -> str:
    """Render the create listing page."""
    return render_template(
        "create_listing.html",
        form_data={},
        categories=listing_service.get_category_options(),
        condition_options=listing_service.get_condition_options(),
    )


@listing_bp.post("/listings/create")
@marketplace_user_required
def create_listing() -> str:
    """Handle listing creation."""
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
@marketplace_user_required
def edit_listing_page(listing_id: int) -> str:
    """Render the edit listing page with pre-filled details."""
    item = listing_service.get_listing_detail(listing_id)
    if not item:
        abort(404)

    if item["seller_id"] != session["user_id"]:
        flash("You are not authorized to edit this item.", "danger")
        return redirect(url_for("listings.view_listing_detail", listing_id=listing_id))

    return render_template(
        "edit_listing.html",
        listing=item,
        listing_image_src=resolve_listing_image_url(item["image_url"]),
        categories=listing_service.get_category_options(),
        condition_options=listing_service.get_condition_options(),
        status_options=listing_service.get_status_options(),
    )


@listing_bp.post("/listings/<int:listing_id>/edit")
@marketplace_user_required
def handle_edit_listing(listing_id: int) -> str:
    """Process data when someone submits changes to their item."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    condition = request.form.get("condition", "").strip()
    status = request.form.get("status", "").strip()

    try:
        price = float(request.form.get("price", ""))
        category_id = int(request.form.get("category_id", ""))
    except ValueError:
        flash("Please enter valid listing information.", "danger")
        return redirect(url_for("listings.edit_listing_page", listing_id=listing_id))

    # Adapted to use Fan Fan's listing_service architecture style
    success = listing_service.edit_listing(
        listing_id,
        session["user_id"],
        category_id,
        title,
        description,
        condition,
        price,
        status,
        request.files.get("image"),
    )
    
    if success:
        flash("Item updated successfully!", "success")
    else:
        flash("Failed to update item. Access denied.", "danger")

    return redirect(url_for("listings.view_listing_detail", listing_id=listing_id))


@listing_bp.post("/listings/<int:listing_id>/delete")
@marketplace_user_required
def delete_listing(listing_id: int) -> str:
    """Delete an item completely if requested by its owner."""
    success = listing_service.delete_listing(listing_id, session["user_id"])
    if success:
        flash("Item was successfully deleted.", "info")
        return redirect(url_for("listings.browse_listings"))

    flash("Failed to delete item. Access denied.", "danger")
    return redirect(url_for("listings.view_listing_detail", listing_id=listing_id))


def _remember_interest_category(category_id: int) -> None:
    """Remember recent category interests for homepage recommendations."""

    _remember_interest_categories([category_id])


def _remember_search_interest_categories(keyword: str, listings) -> None:
    """Remember category interests found from keyword search behaviour."""

    category_ids = listing_service.get_search_interest_category_ids(keyword)
    category_ids.extend(int(listing["category_id"]) for listing in listings)
    _remember_interest_categories(category_ids)


def _remember_interest_categories(category_ids) -> None:
    """Remember recent category interests from browsing or search results."""

    recent_category_ids = session.get("recent_interest_category_ids", [])
    new_category_ids = []
    for category_id in category_ids:
        if category_id > 0 and category_id not in new_category_ids:
            new_category_ids.append(category_id)

    if not new_category_ids:
        return

    recent_category_ids = [
        existing_category_id
        for existing_category_id in recent_category_ids
        if existing_category_id not in new_category_ids
    ]
    session["recent_interest_category_ids"] = (
        new_category_ids + recent_category_ids
    )[:RECENT_INTEREST_LIMIT]
