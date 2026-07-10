"""Administrator routes."""

from flask import Blueprint, flash, redirect, render_template, url_for

from services.admin_service import admin_service
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/admin/users")
@admin_required
def view_users() -> str:
    """Render the administrator user page."""

    return render_template(
        "admin/users.html",
        users=admin_service.get_admin_users(),
    )


@admin_bp.get("/admin/listings")
@admin_required
def view_listings() -> str:
    """Render the administrator listing page."""

    return render_template(
        "admin/listings.html",
        listings=admin_service.get_admin_listings(),
    )


@admin_bp.get("/admin/requests")
@admin_required
def view_requests() -> str:
    """Render the administrator request page."""

    return render_template(
        "admin/requests.html",
        requests=admin_service.get_admin_requests(),
    )


@admin_bp.get("/admin/requests/completed")
@admin_required
def view_completed_requests() -> str:
    """Render the administrator completed request page."""

    return render_template(
        "admin/completed_requests.html",
        requests=admin_service.get_admin_completed_requests(),
    )


@admin_bp.post("/admin/listings/<int:listing_id>/delete")
@admin_required
def delete_inappropriate_listing(listing_id: int) -> str:
    """Handle administrator listing deletion."""

    success, message = admin_service.delete_inappropriate_listing(listing_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.view_listings"))


@admin_bp.post("/admin/users/<int:user_id>/lock")
@admin_required
def lock_user_account(user_id: int) -> str:
    """Handle administrator user lock."""

    success, message = admin_service.lock_user_account(user_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.view_users"))


@admin_bp.post("/admin/users/<int:user_id>/unlock")
@admin_required
def unlock_user_account(user_id: int) -> str:
    """Handle administrator user unlock."""

    success, message = admin_service.unlock_user_account(user_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.view_users"))


@admin_bp.post("/admin/requests/<int:request_id>/lock")
@admin_required
def lock_request_record(request_id: int) -> str:
    """Handle administrator request lock."""

    success, message = admin_service.lock_request_record(request_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.view_requests"))


@admin_bp.post("/admin/requests/<int:request_id>/unlock")
@admin_required
def unlock_request_record(request_id: int) -> str:
    """Handle administrator request unlock."""

    success, message = admin_service.unlock_request_record(request_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.view_requests"))
