"""Reusable decorators for route access control."""

from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view):
    """Require a user session before accessing the route."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login_page"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    """Require an administrator session before accessing the route."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Administrator access is required.", "warning")
            return redirect(url_for("auth.login_page"))
        return view(*args, **kwargs)

    return wrapped_view
