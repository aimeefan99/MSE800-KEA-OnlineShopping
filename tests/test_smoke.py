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
        """Protect the rule that marketplace users can reach the account area."""

        self._login_as(1, ROLE_USER, "Buyer")
        response = self.client.get("/account")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Account", page)
        self.assertIn("Profile", page)
        self.assertIn("My Listings", page)
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
