"""Transaction-related routes for favorites, requests, and reviews."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.transaction_service import transaction_service
from utils.decorators import marketplace_user_required
from utils.listing_images import attach_listing_image_sources

transaction_bp = Blueprint("transactions", __name__)


@transaction_bp.get("/favorites")
@marketplace_user_required
def view_favorites() -> str:
    """Render the favorite list page."""

    favorites = transaction_service.view_favorites(session["user_id"])
    return render_template("favorites.html", favorites=attach_listing_image_sources(favorites))


@transaction_bp.post("/favorites/add")
@marketplace_user_required
def add_favorite() -> str:
    """Handle favorite add action."""

    listing_id = request.form.get("listing_id", type=int)
    if listing_id is None:
        flash("Please choose a valid listing.", "danger")
        return redirect(url_for("listings.browse_listings"))

    message = transaction_service.add_favorite(session["user_id"], listing_id)
    category = "warning" if "already" in message.lower() else "success"
    if "not found" in message.lower():
        category = "danger"
    flash(message, category)
    next_url = request.form.get("next") or url_for(
        "listings.view_listing_detail",
        listing_id=listing_id,
    )
    return redirect(next_url)


@transaction_bp.post("/favorites/remove")
@marketplace_user_required
def remove_favorite() -> str:
    """Handle favorite remove action."""

    return "TODO: remove favorite"


@transaction_bp.post("/requests/create")
@marketplace_user_required
def create_request() -> str:
    """Handle purchase request creation."""

    listing_id = request.form.get("listing_id", type=int)
    if listing_id is None:
        flash("Please choose a valid listing.", "danger")
        return redirect(url_for("listings.browse_listings"))

    success, message = transaction_service.create_request(
        session["user_id"],
        listing_id,
        request.form.get("message", ""),
    )
    flash(message, "success" if success else "warning")
    next_url = request.form.get("next") or url_for(
        "listings.view_listing_detail",
        listing_id=listing_id,
    )
    return redirect(next_url)


@transaction_bp.get("/requests/incoming")
@marketplace_user_required
def incoming_requests() -> str:
    """Render incoming requests page."""

    requests = transaction_service.incoming_requests(session["user_id"])
    return render_template("requests_incoming.html", requests=requests)


@transaction_bp.get("/requests/history")
@marketplace_user_required
def request_history() -> str:
    """Render request history page."""

    request_views = transaction_service.request_history(session["user_id"])
    return render_template(
        "request_history.html",
        outgoing_requests=request_views["outgoing_requests"],
        incoming_requests=request_views["incoming_requests"],
    )


@transaction_bp.post("/requests/<int:request_id>/accept")
@marketplace_user_required
def accept_request(request_id: int) -> str:
    """Handle request acceptance."""

    success, message = transaction_service.accept_request(session["user_id"], request_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("transactions.incoming_requests"))


@transaction_bp.post("/requests/<int:request_id>/reject")
@marketplace_user_required
def reject_request(request_id: int) -> str:
    """Handle request rejection."""

    success, message = transaction_service.reject_request(session["user_id"], request_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("transactions.incoming_requests"))


@transaction_bp.post("/requests/<int:request_id>/complete")
@marketplace_user_required
def complete_request(request_id: int) -> str:
    """Handle transaction completion."""

    success, message = transaction_service.complete_request(session["user_id"], request_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("transactions.request_history"))


@transaction_bp.post("/reviews/create")
@marketplace_user_required
def create_review() -> str:
    """Handle review submission."""

    success, message = transaction_service.create_review(session["user_id"], request.form)
    flash(message, "success" if success else "danger")
    return redirect(url_for("transactions.request_history"))
