"""Reusable decorators for route access control."""

from functools import wraps
from typing import Optional

from flask import flash, redirect, session, url_for

from models.db import get_db
from utils.constants import ROLE_ADMIN, ROLE_USER


def login_required(view):
    """Require a user session before accessing the route."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        # Private pages redirect to login when no session exists.
        redirect_response = _redirect_if_invalid_session()
        if redirect_response is not None:
            return redirect_response
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    """Require an admin session before accessing the route."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        redirect_response = _redirect_if_invalid_session()
        if redirect_response is not None:
            return redirect_response

        if session.get("role") != ROLE_ADMIN or _get_session_user_role() != ROLE_ADMIN:
            flash("Administrator access is required.", "warning")
            return redirect(url_for("auth.login_page"))
        return view(*args, **kwargs)

    return wrapped_view


def marketplace_user_required(view):
    """Require a logged-in non-admin user for marketplace account actions."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        redirect_response = _redirect_if_invalid_session()
        if redirect_response is not None:
            return redirect_response

        if session.get("role") != ROLE_USER or _get_session_user_role() != ROLE_USER:
            flash("This page is only available to marketplace user accounts.", "warning")
            return redirect(url_for("home"))
        return view(*args, **kwargs)

    return wrapped_view


def _redirect_if_invalid_session():
    """Return a redirect response when the current session no longer maps to a valid account."""

    if "user_id" not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for("auth.login_page"))

    user = _get_session_user()
    if user is None:
        session.clear()
        flash("Please log in again to continue.", "warning")
        return redirect(url_for("auth.login_page"))

    if user["is_locked"]:
        session.clear()
        flash("This account is locked.", "danger")
        return redirect(url_for("auth.login_page"))

    return None


def _get_session_user():
    """Load the current session user row from the database."""

    return get_db().execute(
        "SELECT id, role, is_locked FROM users WHERE id = ?",
        (session["user_id"],),
    ).fetchone()


def _get_session_user_role() -> Optional[str]:
    """Return the current user's live role from the database."""

    user = _get_session_user()
    if user is None:
        return None
    return str(user["role"])
