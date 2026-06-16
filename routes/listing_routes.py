"""Listing controller routes for creating, showing, editing, and deleting items."""

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from services.listing_service import (
    browse_listings,
    create_listing,
    delete_listing,
    edit_listing,
    get_listing_detail
)

listing_bp = Blueprint("listings", __name__)


@listing_bp.get("/listings")
def browse_listings_page():
    """Show all items available to browse."""
    items = browse_listings()
    return render_template("listings.html", listings=items)


@listing_bp.get("/listings/<int:listing_id>")
def view_listing_detail_page(listing_id: int):
    """Show the full details of a single item page."""
    item = get_listing_detail(listing_id)
    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("listings.browse_listings_page"))
    return render_template("listing_detail.html", listing=item)


@listing_bp.get("/listings/create")
def create_listing_page():
    """Show the form to post a new product."""
    if "user_id" not in session:
        flash("Please log in first to list an item.", "warning")
        return redirect(url_for("auth.login_page"))
    return render_template("create_listing.html")


@listing_bp.post("/listings/create")
def handle_create_listing():
    """Process form data when a user clicks submit on a new item."""
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    title = request.form.get("title")
    description = request.form.get("description")
    condition = request.form.get("condition")
    price = float(request.form.get("price", 0))
    category_id = int(request.form.get("category_id", 1))

    new_id = create_listing(session["user_id"], category_id, title, description, condition, price)
    flash("Your item has been posted successfully!", "success")
    return redirect(url_for("listings.view_listing_detail_page", listing_id=new_id))


@listing_bp.get("/listings/<int:listing_id>/edit")
def edit_listing_page(listing_id: int):
    """Show the edit page with fields pre-filled with the old data."""
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login_page"))

    item = get_listing_detail(listing_id)
    if not item:
        abort(404)

    if item["seller_id"] != session["user_id"]:
        flash("You are not authorized to edit this item.", "danger")
        return redirect(url_for("listings.view_listing_detail_page", listing_id=listing_id))

    return render_template("edit_listing.html", listing=item)


@listing_bp.post("/listings/<int:listing_id>/edit")
def handle_edit_listing(listing_id: int):
    """Process data when someone submits changes to their item."""
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    title = request.form.get("title")
    description = request.form.get("description")
    condition = request.form.get("condition")
    price = float(request.form.get("price", 0))
    category_id = int(request.form.get("category_id", 1))

    success = edit_listing(
        listing_id,
        session["user_id"],
        category_id,
        title,
        description,
        condition,
        price
    )
    if success:
        flash("Item updated successfully!", "success")
    else:
        flash("Failed to update item. Access denied.", "danger")

    return redirect(url_for("listings.view_listing_detail_page", listing_id=listing_id))


@listing_bp.post("/listings/<int:listing_id>/delete")
def handle_delete_listing(listing_id: int):
    """Delete an item completely if requested by its owner."""
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    success = delete_listing(listing_id, session["user_id"])
    if success:
        flash("Item was successfully deleted.", "info")
        return redirect(url_for("listings.browse_listings_page"))

    flash("Failed to delete item. Access denied.", "danger")
    return redirect(url_for("listings.view_listing_detail_page", listing_id=listing_id))