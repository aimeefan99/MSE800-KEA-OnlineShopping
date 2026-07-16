# Flask Usage Across the System

## Purpose

This document explains how Flask is used in the second-hand trading platform, how route handlers connect browser requests to rendered pages or JSON responses, and where Flask fits in the system architecture.

Flask is the web framework used to receive HTTP requests, run controller logic, call service-layer functions, and return either HTML templates or JSON data. The official Flask documentation describes Flask as a lightweight WSGI web application framework designed to start quickly and scale into more complex applications.

Official reference: https://flask.palletsprojects.com/en/stable/

## Flask Role in This Project

The application is created in `app.py` with `create_app()`. The app factory configures Flask, connects the database teardown hook, registers feature blueprints, and defines the homepage route.

Main Flask responsibilities in the project:

- Route incoming URLs to Python view functions.
- Group related routes using Flask Blueprints.
- Render Jinja templates from the `templates` folder.
- Read form data, query parameters, uploaded files, and session data.
- Redirect users after form submissions.
- Flash success or error messages.
- Return JSON for the homepage recommendation API.
- Apply authentication and role checks through route decorators.

## Application Setup

`app.py` creates the Flask app and registers the route modules:

| Flask component | Project file | Purpose |
| --- | --- | --- |
| `Flask(__name__)` | `app.py` | Creates the web application instance. |
| `app.config.from_object(Config)` | `app.py`, `config.py` | Loads database, S3 image, and secret-key configuration. |
| `app.teardown_appcontext(close_db)` | `app.py`, `models/db.py` | Closes the SQLite connection after each request context. |
| `app.register_blueprint(...)` | `app.py` | Adds modular route groups to the application. |
| `@app.get("/")` | `app.py` | Defines the homepage route. |

## Blueprint Structure

The project separates route files by feature area. This keeps controller code organized and avoids putting all route handlers into `app.py`.

| Blueprint | File | Main responsibility |
| --- | --- | --- |
| `auth_bp` | `routes/auth_routes.py` | Login, registration, logout. |
| `listing_bp` | `routes/listing_routes.py` | Listing browsing, detail view, create, edit, and delete. |
| `transaction_bp` | `routes/transaction_routes.py` | Favorites, purchase requests, request history, reviews. |
| `profile_bp` | `routes/profile_routes.py` | Public profile and edit profile pages. |
| `recommendation_bp` | `routes/recommendation_routes.py` | Homepage recommendation JSON endpoint. |
| `admin_bp` | `routes/admin_routes.py` | Admin listing, user, request, completed request, and lock actions. |
| `ai_bp` | `routes/ai_routes.py` | AI listing draft page and draft generation endpoint. |

## Route-To-Page Mapping

### General Marketplace Routes

| Method | Route | Flask handler | Template or response | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/` | `home()` in `app.py` | `templates/home.html` | Shows the homepage with recent or recommended listings. |
| `GET` | `/listings` | `browse_listings()` | `templates/listings.html` | Shows searchable and filterable marketplace listings. |
| `GET` | `/listings/<listing_id>` | `view_listing_detail()` | `templates/listing_detail.html` | Shows one listing and request/favorite actions. |

### Authentication Routes

| Method | Route | Flask handler | Template or response | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/login` | `login_page()` | `templates/login.html` | Shows the login form. |
| `POST` | `/login` | `login()` | Redirect | Authenticates a user and starts a Flask session. |
| `GET` | `/register` | `register_page()` | `templates/register.html` | Shows the registration form. |
| `POST` | `/register` | `register()` | Redirect | Creates a new user account. |
| `POST` | `/logout` | `logout()` | Redirect | Clears the user session. |

### Listing Management Routes

| Method | Route | Flask handler | Template or response | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/listings/create` | `create_listing_page()` | `templates/create_listing.html` | Shows the sell item form. |
| `POST` | `/listings/create` | `create_listing()` | Redirect | Creates a listing with optional image upload. |
| `GET` | `/listings/<listing_id>/edit` | `edit_listing_page()` | `templates/edit_listing.html` | Shows the edit listing form. |
| `POST` | `/listings/<listing_id>/edit` | `edit_listing()` | Redirect | Saves listing changes. |
| `POST` | `/listings/<listing_id>/delete` | `delete_listing()` | Redirect | Deletes a user-owned listing. |

### Transaction, Request, Favorite, and Review Routes

| Method | Route | Flask handler | Template or response | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/favorites` | `view_favorites()` | `templates/favorites.html` | Shows the signed-in user's saved listings. |
| `POST` | `/favorites/add` | `add_favorite()` | Redirect | Saves a listing to favorites. |
| `POST` | `/favorites/remove` | `remove_favorite()` | Redirect | Removes a listing from favorites. |
| `POST` | `/requests/create` | `create_request()` | Redirect | Creates a buyer request for a listing. |
| `GET` | `/requests/incoming` | `view_incoming_requests()` | `templates/requests_incoming.html` | Shows requests received by a seller. |
| `GET` | `/requests/history` | `view_request_history()` | `templates/request_history.html` | Shows the user's request and transaction history. |
| `POST` | `/requests/<request_id>/accept` | `accept_request()` | Redirect | Seller accepts a purchase request. |
| `POST` | `/requests/<request_id>/reject` | `reject_request()` | Redirect | Seller rejects a purchase request. |
| `POST` | `/requests/<request_id>/complete` | `complete_request()` | Redirect | Marks an accepted request as completed. |
| `POST` | `/reviews/create` | `create_review()` | Redirect | Creates a buyer or seller review after a completed transaction. |

### Profile Routes

| Method | Route | Flask handler | Template or response | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/profiles/<user_id>` | `view_public_profile()` | `templates/profile.html` | Shows a user's public profile, trust indicators, and reviews. |
| `GET` | `/profile/edit` | `edit_profile_page()` | `templates/edit_profile.html` | Shows the signed-in user's editable profile form. |
| `POST` | `/profile/edit` | `edit_profile()` | Redirect | Saves profile changes. |

### Recommendation API Route

| Method | Route | Flask handler | Response | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/recommendations/homepage` | `homepage_recommendations()` | JSON list | Returns homepage listing recommendations based on recent interest and saved categories. |

This route uses Flask's `jsonify()` rather than rendering a page template because it behaves as an API endpoint.

### Administrator Routes

| Method | Route | Flask handler | Template or response | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/admin/listings` | `view_listings()` | `templates/admin/listings.html` | Shows admin listing management records. |
| `GET` | `/admin/users` | `view_users()` | `templates/admin/users.html` | Shows admin user account records. |
| `GET` | `/admin/requests` | `view_requests()` | `templates/admin/requests.html` | Shows admin request records and request lock controls. |
| `GET` | `/admin/requests/completed` | `view_completed_requests()` | `templates/admin/completed_requests.html` | Shows completed request records only. |
| `POST` | `/admin/listings/<listing_id>/delete` | `delete_inappropriate_listing()` | Redirect | Allows an admin to delete a listing. |
| `POST` | `/admin/users/<user_id>/lock` | `lock_user_account()` | Redirect | Locks a marketplace user account. |
| `POST` | `/admin/users/<user_id>/unlock` | `unlock_user_account()` | Redirect | Unlocks a marketplace user account. |
| `POST` | `/admin/requests/<request_id>/lock` | `lock_request_record()` | Redirect | Locks a request record for review. |

### AI Listing Routes

| Method | Route | Flask handler | Template or response | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/ai/listing` | `ai_listing_page()` | `templates/ai_listing.html` | Shows the AI listing draft page. |
| `POST` | `/ai/listing-draft` | `create_listing_draft()` | Template response | Generates a draft listing suggestion. |

## Request Handling Flow

Most browser requests follow this pattern:

1. The browser sends a request to a Flask route.
2. The route handler validates access using decorators such as `login_required`, `marketplace_user_required`, or `admin_required`.
3. The route reads request data from `request.args`, `request.form`, `request.files`, or `session`.
4. The route calls a service class such as `listing_service`, `transaction_service`, `profile_service`, or `admin_service`.
5. The service interacts with SQLite through `models/db.py`.
6. The route returns `render_template()`, `redirect()`, or `jsonify()`.
7. The Jinja template extends `templates/base.html` and renders the final HTML page.

## Template Rendering

Flask renders HTML through Jinja templates in the `templates` directory. The shared page layout is stored in `templates/base.html`, and feature pages extend it with `{% extends "base.html" %}`.

Examples:

- `home.html` renders homepage recommendations.
- `listings.html` renders marketplace browse results.
- `listing_detail.html` renders one listing with request and favorite actions.
- `request_history.html` renders sent, incoming, and completed transaction history.
- `profile.html` renders public profile trust indicators and reviews.
- `admin/_request_table.html` is a reusable partial used by admin request pages.

## Session Usage

Flask sessions are used to remember the signed-in user's identity and role. The project stores values such as:

- `session["user_id"]`
- `session["role"]`
- `session["display_name"]`
- `session["recent_interest_category_ids"]`

These session values support authentication, role-based navigation, marketplace access control, and homepage recommendation personalization.

## Redirects and Flash Messages

Form submissions usually return redirects rather than directly rendering the next page. This follows the post-redirect-get pattern and prevents duplicate submissions when the browser refreshes.

The project also uses Flask flash messages to show success or error feedback after actions such as login, listing creation, request actions, reviews, admin deletion, and request locking.

## Access Control

Access control is applied at the route level with decorators from `utils/decorators.py`.

| Decorator | Purpose |
| --- | --- |
| `login_required` | Requires a signed-in user. |
| `marketplace_user_required` | Allows normal marketplace users and blocks admin-only accounts. |
| `admin_required` | Allows administrator users only. |

This means Flask routes are not only URL mappings; they also enforce which type of user may access each platform workflow.

## Official Flask References

The project mainly relies on these Flask concepts:

- Flask documentation homepage: https://flask.palletsprojects.com/en/stable/
- Routing: https://flask.palletsprojects.com/en/stable/quickstart/#routing
- Blueprints: https://flask.palletsprojects.com/en/stable/blueprints/
- Templates: https://flask.palletsprojects.com/en/stable/templating/
- Sessions: https://flask.palletsprojects.com/en/stable/quickstart/#sessions
- Testing Flask applications: https://flask.palletsprojects.com/en/stable/testing/

## Summary

Flask is the central web framework connecting the user interface, route controllers, service layer, database access, and templates. The implemented platform uses Flask Blueprints to keep feature areas modular, Jinja templates to render pages, sessions to manage signed-in user context, decorators to enforce access rules, redirects and flash messages for form workflows, and JSON responses for recommendation API behavior.
