"""Application entry point for the second-hand trading platform."""

from flask import Flask, render_template

from config import Config
from models.db import close_db
from routes.admin_routes import admin_bp
from routes.ai_routes import ai_bp
from routes.auth_routes import auth_bp
from routes.listing_routes import listing_bp
from routes.profile_routes import profile_bp
from routes.recommendation_routes import recommendation_bp
from routes.transaction_routes import transaction_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object(Config)
    app.teardown_appcontext(close_db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(listing_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(admin_bp)

    @app.get("/")
    def home() -> str:
        """Render the homepage."""

        return render_template("home.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
