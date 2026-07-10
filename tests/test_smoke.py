"""Smoke tests for the most important shared platform rules.

Run with:
    python -m unittest -v tests.test_smoke

This file protects a few core guardrails that are easy to break during parallel development:
- admin accounts must stay out of marketplace-only pages
- normal users must stay out of admin pages
- sold listings must stay out of normal public browse results
- the same listing must not be favorited twice by the same user
- public profiles must show public contact details without exposing full legal names
"""

import sqlite3
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models.schema import SCHEMA
from utils.constants import (
    CONTACT_METHOD_EMAIL,
    LISTING_STATUS_AVAILABLE,
    LISTING_STATUS_SOLD,
    ROLE_ADMIN,
    ROLE_USER,
)


class SmokeTestCase(unittest.TestCase):
    """Verify the smallest set of rules that should never silently regress."""

    def setUp(self) -> None:
        """Create an isolated application and SQLite database for each test."""

        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.upload_dir = Path(self.temp_dir.name) / "uploads"
        self.legacy_upload_dir = Path(self.temp_dir.name) / "legacy_uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.legacy_upload_dir.mkdir(parents=True, exist_ok=True)

        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret",
            DATABASE_PATH=self.database_path,
            UPLOAD_FOLDER=self.upload_dir,
            LEGACY_UPLOAD_FOLDER=self.legacy_upload_dir,
        )
        self.client = self.app.test_client()

        self._initialize_database()

    def tearDown(self) -> None:
        """Clean up the temporary workspace used by the test."""

        self.temp_dir.cleanup()

    def test_brand_rule_header_uses_kea_marketplace_logo(self) -> None:
        """Protect the rule that the shared header uses the branded logo."""

        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>Kea Marketplace</title>", page)
        self.assertIn("kea-marketplace-logo.png", page)
        self.assertIn("Kea Marketplace", page)
        self.assertNotIn("Second-Hand Trading Platform", page)

    def test_access_rule_admin_cannot_open_marketplace_only_pages(self) -> None:
        """Protect the rule that admin accounts do not participate in trading flows."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        for path in [
            "/account",
            "/account/listings",
            "/profile/edit",
            "/favorites",
            "/listings/create",
            "/requests/history",
        ]:
            response = self.client.get(path, follow_redirects=False)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers["Location"], "/")

    def test_access_rule_marketplace_user_cannot_open_admin_pages(self) -> None:
        """Protect the rule that marketplace users cannot enter admin management pages."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.get("/admin/listings", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")

    def test_access_rule_locked_user_cannot_keep_using_marketplace_pages(self) -> None:
        """Protect the rule that a locked account cannot continue using an old session."""

        connection = sqlite3.connect(self.database_path)
        connection.execute("UPDATE users SET is_locked = 1 WHERE id = 1")
        connection.commit()
        connection.close()

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.get("/favorites", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")

    def test_access_rule_session_role_must_match_live_admin_role(self) -> None:
        """Protect the rule that admin access must be confirmed against the database."""

        self._login_as(1, ROLE_ADMIN, "Buyer")
        response = self.client.get("/admin/listings", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")

    def test_admin_users_page_lists_user_accounts(self) -> None:
        """Protect the rule that the admin user page shows account records."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.get("/admin/users")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("User Management", page)
        self.assertIn("buyer@example.com", page)
        self.assertIn("admin@example.com", page)

    def test_admin_pages_show_summary_cards_and_filter_tables(self) -> None:
        """Protect admin summary cards and table filtering controls."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        self.client.post("/admin/users/1/lock")

        users_response = self.client.get("/admin/users?status=locked")
        users_page = users_response.get_data(as_text=True)
        listings_response = self.client.get("/admin/listings?status=sold")
        listings_page = listings_response.get_data(as_text=True)

        self.assertEqual(users_response.status_code, 200)
        self.assertIn("Total Users", users_page)
        self.assertIn("Locked Users", users_page)
        self.assertIn("Active Listings", users_page)
        self.assertIn("Completed Requests", users_page)
        self.assertIn("buyer@example.com", users_page)
        self.assertNotIn("admin@example.com", users_page)

        self.assertEqual(listings_response.status_code, 200)
        self.assertIn("Sold Bike", listings_page)
        self.assertNotIn("Available Camera", listings_page)

    def test_status_badges_use_consistent_colour_classes(self) -> None:
        """Protect status badge colour classes across listings and requests."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        listings_page = self.client.get("/admin/listings").get_data(as_text=True)
        requests_page = self.client.get("/admin/requests").get_data(as_text=True)
        completed_page = self.client.get(
            "/admin/requests/completed",
        ).get_data(as_text=True)

        self.assertIn("status-badge--available", listings_page)
        self.assertIn("status-badge--sold", listings_page)
        self.assertIn("status-badge--pending", requests_page)
        self.assertIn("status-badge--completed", completed_page)

        self.client.post("/admin/requests/1/lock")
        locked_page = self.client.get("/admin/requests").get_data(as_text=True)
        self.assertIn("status-badge--locked", locked_page)

    def test_theme_styles_alerts_with_kea_feedback_colours(self) -> None:
        """Protect themed flash and status alert styles."""

        stylesheet = (PROJECT_ROOT / "static" / "css" / "main.css").read_text()

        self.assertIn(".alert-success", stylesheet)
        self.assertIn(".alert-danger", stylesheet)
        self.assertIn(".alert-warning", stylesheet)
        self.assertIn(".alert-info", stylesheet)
        self.assertIn("box-shadow: 0 0.65rem 1.25rem var(--kea-shadow);", stylesheet)

    def test_admin_user_rule_admin_can_lock_marketplace_user_account(self) -> None:
        """Protect the rule that administrators can lock unsafe user accounts."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.post(
            "/admin/users/1/lock",
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("User account locked.", page)
        self.assertIn("Locked", page)
        self.assertEqual(1, self._get_user_lock_status(1))

        self._login_as(1, ROLE_USER, "Buyer")
        blocked_response = self.client.get("/favorites", follow_redirects=False)
        self.assertEqual(blocked_response.status_code, 302)
        self.assertEqual(blocked_response.headers["Location"], "/login")

    def test_admin_user_rule_admin_accounts_are_protected_from_user_lock(self) -> None:
        """Protect the rule that administrator accounts cannot be locked this way."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.post(
            "/admin/users/2/lock",
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Administrator accounts cannot be changed from this page.", page)
        self.assertEqual(0, self._get_user_lock_status(2))

    def test_admin_user_rule_admin_can_unlock_marketplace_user_account(self) -> None:
        """Protect the rule that administrators can reopen locked user accounts."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        self.client.post("/admin/users/1/lock")
        response = self.client.post(
            "/admin/users/1/unlock",
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("User account unlocked.", page)
        self.assertIn("Active", page)
        self.assertEqual(0, self._get_user_lock_status(1))

    def test_admin_delete_rule_admin_can_remove_listing_from_management(self) -> None:
        """Protect the rule that administrators can delete inappropriate listings."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.post(
            "/admin/listings/1/delete",
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Listing deleted successfully.", page)
        self.assertNotIn("Available Camera", self.client.get("/listings").get_data(as_text=True))

    def test_admin_delete_rule_marketplace_user_cannot_delete_listing(self) -> None:
        """Protect the rule that normal users cannot use admin deletion actions."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.post("/admin/listings/1/delete", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")

    def test_admin_request_rule_admin_can_view_request_records(self) -> None:
        """Protect the rule that administrators can review request records."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.get("/admin/requests")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Request Management", page)

    def test_admin_request_records_page_lists_request_activity(self) -> None:
        """Protect the rule that administrators can monitor request records."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.get("/admin/requests")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Request Management", page)
        self.assertIn("Available Camera", page)
        self.assertIn("Sold Bike", page)
        self.assertIn("Open", page)
        self.assertIn("Pending", page)
        self.assertIn("Completed", page)

    def test_admin_request_rule_admin_can_lock_request_without_changing_result(self) -> None:
        """Protect the rule that request locks freeze records without status changes."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.post(
            "/admin/requests/1/lock",
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Request record locked for review.", page)
        self.assertIn("Locked", page)
        self.assertEqual("accepted", self._get_request_status(1))

    def test_admin_request_rule_admin_can_unlock_request_record(self) -> None:
        """Protect the rule that administrators can reopen locked request records."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        self.client.post("/admin/requests/1/lock")
        response = self.client.post(
            "/admin/requests/1/unlock",
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Request record unlocked.", page)
        self.assertIn("Open", page)
        self.assertEqual("accepted", self._get_request_status(1))

    def test_admin_request_rule_locked_request_cannot_be_completed(self) -> None:
        """Protect the rule that locked request records cannot keep changing."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        self.client.post("/admin/requests/1/lock")

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.post(
            "/requests/1/complete",
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("This request is locked and cannot be changed.", page)
        self.assertEqual("accepted", self._get_request_status(1))

    def test_review_rule_completed_transaction_can_be_reviewed_once(self) -> None:
        """Protect the rule that completed transactions can receive one review."""

        self._login_as(1, ROLE_USER, "Buyer")
        first_response = self.client.post(
            "/reviews/create",
            data={
                "request_id": 2,
                "reviewed_user_id": 3,
                "score": 5,
                "comment": "Smooth trade.",
            },
            follow_redirects=True,
        )
        second_response = self.client.post(
            "/reviews/create",
            data={
                "request_id": 2,
                "reviewed_user_id": 3,
                "score": 5,
                "comment": "Smooth trade.",
            },
            follow_redirects=True,
        )

        self.assertIn("Review submitted successfully.", first_response.get_data(as_text=True))
        self.assertIn(
            "You have already reviewed this completed transaction.",
            second_response.get_data(as_text=True),
        )
        self.assertEqual(1, self._get_review_count())

    def test_review_rule_locked_completed_transaction_cannot_be_reviewed(self) -> None:
        """Protect the rule that locked requests cannot receive new reviews."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        self.client.post("/admin/requests/2/lock")

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.post(
            "/reviews/create",
            data={
                "request_id": 2,
                "reviewed_user_id": 3,
                "score": 5,
                "comment": "Smooth trade.",
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)

        self.assertIn("This request is locked and cannot be reviewed.", page)
        self.assertEqual(0, self._get_review_count())

    def test_review_rule_non_completed_transaction_cannot_be_reviewed(self) -> None:
        """Protect the rule that reviews are limited to completed transactions."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.post(
            "/reviews/create",
            data={
                "request_id": 1,
                "reviewed_user_id": 3,
                "score": 5,
                "comment": "Trying too early.",
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)

        self.assertIn("Only completed transactions can be reviewed.", page)
        self.assertEqual(0, self._get_review_count())

    def test_admin_completed_request_records_page_lists_only_completed_activity(self) -> None:
        """Protect the rule that administrators can monitor completed transactions."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.get("/admin/requests/completed")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Completed Request Records", page)
        self.assertIn("Sold Bike", page)
        self.assertIn("Completed", page)
        self.assertNotIn("Available Camera", page)
        self.assertNotIn("Pending", page)

    def test_browse_rule_public_list_page_hides_sold_listings(self) -> None:
        """Protect the rule that sold items stay out of normal browse results."""

        response = self.client.get("/listings")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Available Camera", page)
        self.assertNotIn("Sold Bike", page)

    def test_request_history_rule_tracks_user_activity(self) -> None:
        """Protect the rule that users can track request and transaction activity."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.get("/requests/history")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sent Requests", page)
        self.assertIn("Incoming Requests", page)
        self.assertIn("Completed Transactions", page)
        self.assertIn("Sold Bike", page)
        self.assertIn("Completed", page)

    def test_account_rule_marketplace_user_can_open_account_page(self) -> None:
        """Protect the rule that account opens the user's public profile first."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.get("/account")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Public Profile", page)
        self.assertIn("Buyer", page)
        self.assertIn("Edit Profile", page)
        self.assertIn("My Listings", page)
        self.assertNotIn("Save Changes", page)

    def test_account_rule_edit_profile_page_keeps_form_separate(self) -> None:
        """Protect the rule that profile edits stay behind the edit action."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.get("/profile/edit")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("My Profile", page)
        self.assertIn("Save Changes", page)

    def test_account_rule_my_listings_page_shows_only_owned_items(self) -> None:
        """Protect the rule that users only manage listings they created."""

        self._login_as(3, ROLE_USER, "Seller")
        response = self.client.get("/account/listings")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("My Listings", page)
        self.assertIn("Available Camera", page)
        self.assertIn("Sold Bike", page)
        self.assertIn("Available Tennis Racket", page)
        self.assertIn("Delete", page)
        self.assertIn("Open the listing detail page to review or edit this item.", page)

    def test_account_rule_buyer_sees_empty_state_when_no_owned_listings_exist(self) -> None:
        """Protect the empty-state path for marketplace users without listings."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.get("/account/listings")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("No listings created yet", page)
        self.assertNotIn("Available Camera", page)

    def test_empty_states_include_useful_next_actions(self) -> None:
        """Protect empty states so users are not left on dead-end pages."""

        self._login_as(1, ROLE_USER, "Buyer")
        favorites_page = self.client.get("/favorites").get_data(as_text=True)
        listings_page = self.client.get("/account/listings").get_data(as_text=True)

        connection = sqlite3.connect(self.database_path)
        connection.execute("DELETE FROM requests")
        connection.commit()
        connection.close()
        requests_page = self.client.get("/requests/history").get_data(as_text=True)

        self.assertIn("No favourites yet", favorites_page)
        self.assertIn("Browse Listings", favorites_page)
        self.assertIn("No listings created yet", listings_page)
        self.assertIn("Create Listing", listings_page)
        self.assertIn("No requests yet", requests_page)
        self.assertIn("Browse Listings", requests_page)

    def test_listing_rule_expanded_category_options_are_available(self) -> None:
        """Protect the rule that second-hand categories cover common item types."""

        expected_categories = [
            "Home &amp; Living",
            "Clothing &amp; Fashion",
            "Books &amp; Media",
            "Beauty &amp; Health",
            "Hobbies &amp; Toys",
            "Vehicles &amp; Bicycles",
            "Other",
        ]

        browse_response = self.client.get("/listings")
        browse_page = browse_response.get_data(as_text=True)
        self._login_as(3, ROLE_USER, "Seller")
        create_response = self.client.get("/listings/create")
        create_page = create_response.get_data(as_text=True)

        self.assertEqual(browse_response.status_code, 200)
        self.assertEqual(create_response.status_code, 200)
        for category in expected_categories:
            self.assertIn(category, browse_page)
            self.assertIn(category, create_page)

    def test_listing_rule_owner_can_replace_listing_image(self) -> None:
        """Protect the rule that sellers can upload a new image when editing a listing."""

        self._login_as(3, ROLE_USER, "Seller")
        original_image_url = self._get_listing_image_url(1)
        response = self.client.post(
            "/listings/1/edit",
            data={
                "title": "Available Camera",
                "category_id": "1",
                "price": "1000.00",
                "condition": "used",
                "status": "available",
                "description": "Good camera listing",
                "image": (BytesIO(b"replacement-image"), "camera-updated.jpg"),
            },
            content_type="multipart/form-data",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(original_image_url, self._get_listing_image_url(1))

    def test_listing_rule_owner_detail_page_hides_favorite_action(self) -> None:
        """Protect the rule that sellers do not favorite their own listings."""

        self._login_as(3, ROLE_USER, "Seller")
        response = self.client.get("/listings/1")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Back to My Listings", page)
        self.assertNotIn("Add to Favorites", page)

    def test_homepage_rule_uses_recent_category_interest(self) -> None:
        """Protect the rule that recent browsing improves homepage recommendations."""

        self.client.get("/listings?category_id=2")
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Recommended from your recent browsing", page)
        self.assertIn("Sports &amp; Outdoors", page)
        self.assertIn("Available Tennis Racket", page)
        self.assertNotIn("Sold Bike", page)

    def test_homepage_rule_uses_recent_keyword_search_interest(self) -> None:
        """Protect the rule that recent search behaviour improves recommendations."""

        self.client.get("/listings?keyword=cloting")
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Recommended from your recent browsing", page)
        self.assertIn("Clothing &amp; Fashion", page)
        self.assertNotIn("Sold Bike", page)

    def test_homepage_rule_uses_common_search_term_categories(self) -> None:
        """Protect the rule that common item searches map to useful categories."""

        self.client.get("/listings?keyword=camera")
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Electronics", page)
        self.assertIn("Available Camera", page)

    def test_recommendation_api_returns_listing_results_only(self) -> None:
        """Protect the documented recommendation endpoint response shape."""

        self.client.get("/listings?category_id=1")
        self.client.get("/listings?category_id=2")
        response = self.client.get("/recommendations/homepage")
        listings = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(listings, list)
        self.assertEqual("Available Tennis Racket", listings[0]["title"])
        self.assertEqual("Available Laptop", listings[1]["title"])
        self.assertNotIn("is_personalized", response.get_data(as_text=True))

    def test_homepage_rule_uses_favorite_categories(self) -> None:
        """Protect the rule that saved item categories improve recommendations."""

        self._login_as(1, ROLE_USER, "Buyer")
        self.client.post("/favorites/add", data={"listing_id": 1, "next": "/"})
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Electronics", page)
        self.assertIn("Available Camera", page)

    def test_favorite_rule_same_listing_cannot_be_saved_twice(self) -> None:
        """Protect the rule that favorites are unique per user and listing."""

        self._login_as(1, ROLE_USER, "Buyer")
        first_response = self.client.post(
            "/favorites/add",
            data={"listing_id": 1, "next": "/listings/1"},
            follow_redirects=True,
        )
        second_response = self.client.post(
            "/favorites/add",
            data={"listing_id": 1, "next": "/listings/1"},
            follow_redirects=True,
        )
        self.assertIn("Listing added to favorites.", first_response.get_data(as_text=True))
        self.assertIn(
            "This listing is already in your favorites.",
            second_response.get_data(as_text=True),
        )

    def test_profile_rule_public_profile_hides_full_name_but_shows_public_contact(self) -> None:
        """Protect the rule that only public profile fields are shown to other users."""

        response = self.client.get("/profiles/1")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("buyer@example.com", page)
        self.assertNotIn("Buyer Legal Name", page)

    def test_profile_rule_public_profile_shows_trust_indicators(self) -> None:
        """Protect the rule that public profiles show reliability indicators."""

        self._login_as(1, ROLE_USER, "Buyer")
        self.client.post(
            "/reviews/create",
            data={
                "request_id": 2,
                "reviewed_user_id": 3,
                "score": 5,
                "comment": "Smooth trade.",
            },
        )

        response = self.client.get("/profiles/3")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Completed Trades", page)
        self.assertIn("Average Rating", page)
        self.assertIn("Positive Feedback", page)
        self.assertIn("Reviews", page)
        self.assertIn("1", page)
        self.assertIn("5.0", page)
        self.assertIn("100%", page)
        self.assertIn("Smooth trade.", page)

    def test_ai_draft_route_requires_an_uploaded_image(self) -> None:
        """Protect the automatic draft route so empty requests fail cleanly."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.post("/ai/listing-draft")
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(payload["success"])
        self.assertIn("Please upload one product image first.", payload["error"])

    def _login_as(self, user_id: int, role: str, display_name: str) -> None:
        """Write a test session for the selected account."""

        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["role"] = role
            session["display_name"] = display_name

    def _get_request_status(self, request_id: int) -> str:
        """Return a request status directly from the isolated test database."""

        connection = sqlite3.connect(self.database_path)
        request = connection.execute(
            "SELECT status FROM requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        connection.close()
        return request[0]

    def _get_user_lock_status(self, user_id: int) -> int:
        """Return the user lock flag from the isolated test database."""

        connection = sqlite3.connect(self.database_path)
        user = connection.execute(
            "SELECT is_locked FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        connection.close()
        return user[0]

    def _get_review_count(self) -> int:
        """Return the number of reviews in the isolated test database."""

        connection = sqlite3.connect(self.database_path)
        review_count = connection.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        connection.close()
        return review_count

    def _get_listing_image_url(self, listing_id: int) -> str:
        """Return a listing image path directly from the isolated test database."""

        connection = sqlite3.connect(self.database_path)
        listing = connection.execute(
            "SELECT image_url FROM listings WHERE id = ?",
            (listing_id,),
        ).fetchone()
        connection.close()
        return listing[0]

    def _initialize_database(self) -> None:
        """Create the schema and seed the smallest useful demo dataset."""

        connection = sqlite3.connect(self.database_path)
        connection.executescript(SCHEMA)
        connection.executemany(
            """
            INSERT INTO users (
                id,
                display_name,
                full_name,
                date_of_birth,
                email,
                phone_number,
                preferred_contact_method,
                password_hash,
                role,
                is_locked,
                bio,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    1,
                    "Buyer",
                    "Buyer Legal Name",
                    "1990-01-01",
                    "buyer@example.com",
                    None,
                    CONTACT_METHOD_EMAIL,
                    "hashed-password",
                    ROLE_USER,
                    0,
                    "Buyer bio",
                    "2026-06-01T10:00:00",
                ),
                (
                    2,
                    "Admin",
                    "Platform Administrator",
                    "1990-01-01",
                    "admin@example.com",
                    None,
                    CONTACT_METHOD_EMAIL,
                    "hashed-password",
                    ROLE_ADMIN,
                    0,
                    "Admin bio",
                    "2026-06-01T10:00:00",
                ),
                (
                    3,
                    "Seller",
                    "Seller Legal Name",
                    "1991-02-02",
                    "seller@example.com",
                    None,
                    CONTACT_METHOD_EMAIL,
                    "hashed-password",
                    ROLE_USER,
                    0,
                    "Seller bio",
                    "2026-06-01T10:00:00",
                ),
            ],
        )
        connection.executemany(
            "INSERT INTO categories (id, name) VALUES (?, ?)",
            [(1, "Electronics"), (2, "Sports & Outdoors")],
        )
        connection.executemany(
            """
            INSERT INTO listings (
                id,
                seller_id,
                category_id,
                image_url,
                title,
                description,
                condition,
                price,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    1,
                    3,
                    1,
                    "uploads/missing-camera.jpg",
                    "Available Camera",
                    "Good camera listing",
                    "used",
                    1000.0,
                    LISTING_STATUS_AVAILABLE,
                    "2026-06-05T10:00:00",
                    "2026-06-05T10:00:00",
                ),
                (
                    2,
                    3,
                    2,
                    "uploads/missing-bike.jpg",
                    "Sold Bike",
                    "Already sold bike listing",
                    "used",
                    250.0,
                    LISTING_STATUS_SOLD,
                    "2026-06-04T09:00:00",
                    "2026-06-04T09:00:00",
                ),
                (
                    4,
                    3,
                    1,
                    "uploads/missing-laptop.jpg",
                    "Available Laptop",
                    "Newer electronics listing",
                    "used",
                    700.0,
                    LISTING_STATUS_AVAILABLE,
                    "2026-06-07T10:00:00",
                    "2026-06-07T10:00:00",
                ),
                (
                    3,
                    3,
                    2,
                    "uploads/missing-racket.jpg",
                    "Available Tennis Racket",
                    "Lightweight sports racket",
                    "used",
                    45.0,
                    LISTING_STATUS_AVAILABLE,
                    "2026-06-06T10:00:00",
                    "2026-06-06T10:00:00",
                ),
            ],
        )
        connection.executemany(
            """
            INSERT INTO requests (
                id,
                listing_id,
                buyer_id,
                seller_id,
                status,
                is_locked,
                message,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    1,
                    1,
                    1,
                    3,
                    "accepted",
                    0,
                    "Please hold this for review.",
                    "2026-06-07T10:00:00",
                    "2026-06-07T10:00:00",
                ),
                (
                    2,
                    2,
                    1,
                    3,
                    "completed",
                    0,
                    "Completed bike purchase",
                    "2026-06-08T10:00:00",
                    "2026-06-08T10:00:00",
                ),
                (
                    3,
                    1,
                    1,
                    3,
                    "pending",
                    0,
                    "Interested in the camera",
                    "2026-06-09T10:00:00",
                    "2026-06-09T10:00:00",
                ),
            ],
        )
        connection.commit()
        connection.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
