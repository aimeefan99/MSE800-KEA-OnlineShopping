"""Administrator routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from services.admin_service import admin_service
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/admin/users")
@admin_required
def view_users() -> str:
    """Render the administrator user page."""

    filters = {
        "role": request.args.get("role", ""),
        "status": request.args.get("status", ""),
    }
    return render_template(
        "admin/users.html",
        admin_summary=admin_service.get_admin_summary(),
        filters=filters,
        users=admin_service.get_admin_users(filters),
    )


@admin_bp.get("/admin/listings")
@admin_required
def view_listings() -> str:
    """Render the administrator listing page."""

    filters = {
        "status": request.args.get("status", ""),
        "category": request.args.get("category", ""),
    }
    return render_template(
        "admin/listings.html",
        admin_summary=admin_service.get_admin_summary(),
        category_options=admin_service.get_listing_category_filter_options(),
        filters=filters,
        listings=admin_service.get_admin_listings(filters),
        status_options=admin_service.get_listing_status_filter_options(),
    )


@admin_bp.get("/admin/requests")
@admin_required
def view_requests() -> str:
    """Render the administrator request page."""

    filters = {
        "status": request.args.get("status", ""),
        "lock": request.args.get("lock", ""),
    }
    return render_template(
        "admin/requests.html",
        admin_summary=admin_service.get_admin_summary(),
        filters=filters,
        requests=admin_service.get_admin_requests(filters),
        status_options=admin_service.get_request_status_filter_options(),
    )


@admin_bp.get("/admin/requests/completed")
@admin_required
def view_completed_requests() -> str:
    """Render the administrator completed request page."""

    filters = {
        "lock": request.args.get("lock", ""),
    }
    return render_template(
        "admin/completed_requests.html",
        admin_summary=admin_service.get_admin_summary(),
        filters=filters,
        requests=admin_service.get_admin_completed_requests(filters),
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
