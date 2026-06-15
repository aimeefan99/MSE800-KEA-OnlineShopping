"""Authentication routes."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.auth_service import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login_page() -> str:
    """Render the login page."""

    return render_template("login.html", form_data={})


@auth_bp.post("/login")
def login() -> str:
    """Handle login submission."""

    user, error_message = auth_service.login_user(request.form)
    if error_message is not None:
        flash(error_message, "danger")
        return render_template("login.html", form_data=request.form)

    # Reset any old session data before storing the current login state.
    session.clear()
    session.update(auth_service.build_session_data(user))
    flash("Logged in successfully.", "success")
    return redirect(url_for("home"))


@auth_bp.get("/register")
def register_page() -> str:
    """Render the register page."""

    return render_template("register.html", form_data={})


@auth_bp.post("/register")
def register() -> str:
    """Handle register submission."""

    # Keep the route thin by delegating validation and persistence to the service.
    success, error_message = auth_service.register_user(request.form)
    if not success:
        flash(error_message, "danger")
        return render_template("register.html", form_data=request.form)

    # Redirect to login after a successful registration so the next step is explicit.
    flash("Account created successfully. Please log in.", "success")
    return redirect(url_for("auth.login_page"))


@auth_bp.post("/logout")
def logout() -> str:
    """Handle logout submission."""

    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))
