"""Application entry point for the second-hand trading platform."""

from flask import Flask, render_template, session

from config import Config
from models.db import close_db
from routes.admin_routes import admin_bp
from routes.ai_routes import ai_bp
from routes.auth_routes import auth_bp
from routes.listing_routes import listing_bp
from routes.profile_routes import profile_bp
from routes.recommendation_routes import recommendation_bp
from routes.transaction_routes import transaction_bp
from services.recommendation_service import recommendation_service
from utils.listing_images import attach_listing_image_sources


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object(Config)
    app.teardown_appcontext(close_db)

    # Register feature blueprints here so routes stay grouped by responsibility.
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

        recommendations = recommendation_service.get_homepage_recommendations(
            session.get("recent_interest_category_ids", []),
            session.get("user_id"),
        )
        recommendations["listings"] = attach_listing_image_sources(
            recommendations["listings"]
        )
        return render_template("home.html", recommendations=recommendations)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
        debug=app.config["DEBUG"],
    )
