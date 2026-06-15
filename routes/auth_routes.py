"""Authentication routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from services.auth_service import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login_page() -> str:
    """Render the login page."""

    return render_template("login.html")


@auth_bp.post("/login")
def login() -> str:
    """Handle login submission."""

    return "TODO: login"


@auth_bp.get("/register")
def register_page() -> str:
    """Render the register page."""

    return render_template("register.html", form_data={})


@auth_bp.post("/register")
def register() -> str:
    """Handle register submission."""

    success, error_message = auth_service.register_user(request.form)
    if not success:
        flash(error_message, "danger")
        return render_template("register.html", form_data=request.form)

    flash("Account created successfully. Please log in.", "success")
    return redirect(url_for("auth.login_page"))


@auth_bp.post("/logout")
def logout() -> str:
    """Handle logout submission."""

    return "TODO: logout"
