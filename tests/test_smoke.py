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
        for path in ["/profile/edit", "/favorites", "/listings/create", "/requests/history"]:
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

    def test_admin_request_records_page_lists_request_activity(self) -> None:
        """Protect the rule that administrators can monitor request records."""

        self._login_as(2, ROLE_ADMIN, "Admin")
        response = self.client.get("/admin/requests")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Request Records", page)
        self.assertIn("Available Camera", page)
        self.assertIn("Sold Bike", page)
        self.assertIn("Pending", page)
        self.assertIn("Completed", page)

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

        self.client.get("/listings?category_id=2")
        response = self.client.get("/recommendations/homepage")
        listings = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(listings, list)
        self.assertEqual("Available Tennis Racket", listings[0]["title"])
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
        """Protect the rule that public profiles show practical trust information."""

        response = self.client.get("/profiles/3")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Completed Transactions", page)
        self.assertIn(">1<", page)
        self.assertIn("Average Rating", page)
        self.assertIn("5.0 / 5", page)
        self.assertIn("100% positive", page)
        self.assertIn("Smooth completed sale.", page)

    def test_review_rule_completed_transaction_can_be_reviewed_once(self) -> None:
        """Protect the rule that reviews can be submitted after completed transactions."""

        self._login_as(3, ROLE_USER, "Seller")
        first_response = self.client.post(
            "/reviews/create",
            data={
                "request_id": 2,
                "reviewed_user_id": 1,
                "score": 4,
                "comment": "Prompt buyer.",
            },
            follow_redirects=True,
        )
        second_response = self.client.post(
            "/reviews/create",
            data={
                "request_id": 2,
                "reviewed_user_id": 1,
                "score": 4,
                "comment": "Prompt buyer.",
            },
            follow_redirects=True,
        )

        self.assertIn("Review submitted successfully.", first_response.get_data(as_text=True))
        self.assertIn(
            "You have already reviewed this transaction.",
            second_response.get_data(as_text=True),
        )

    def _login_as(self, user_id: int, role: str, display_name: str) -> None:
        """Write a test session for the selected account."""

        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["role"] = role
            session["display_name"] = display_name

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
                    "pending",
                    0,
                    "Interested in the camera",
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
            ],
        )
        connection.executemany(
            """
            INSERT INTO reviews (
                id,
                request_id,
                reviewer_id,
                reviewed_user_id,
                score,
                comment,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    1,
                    2,
                    1,
                    3,
                    5,
                    "Smooth completed sale.",
                    "2026-06-09T10:00:00",
                ),
            ],
        )
        connection.commit()
        connection.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
