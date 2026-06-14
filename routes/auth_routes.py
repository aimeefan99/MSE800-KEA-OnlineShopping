"""Authentication routes."""

from flask import Blueprint, render_template

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

    return render_template("register.html")


@auth_bp.post("/register")
def register() -> str:
    """Handle register submission."""

    return "TODO: register"


@auth_bp.post("/logout")
def logout() -> str:
    """Handle logout submission."""

    return "TODO: logout"
