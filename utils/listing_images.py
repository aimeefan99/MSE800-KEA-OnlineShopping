"""Helpers for resolving listing image sources across templates."""

from pathlib import Path
from typing import Any, Dict, List

from flask import current_app, url_for


def attach_listing_image_sources(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Attach a resolved image URL to each listing-like dictionary."""

    for listing in listings:
        listing["image_src"] = resolve_listing_image_url(listing.get("image_url"))
    return listings


def resolve_listing_image_url(image_url: str) -> str:
    """Return a browser-safe image URL for local uploads or remote storage."""

    if not image_url:
        return url_for("static", filename="images/listing-placeholder.svg")

    if image_url.startswith(("http://", "https://")):
        return image_url

    normalized_filename = strip_upload_prefix(image_url)
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    if (upload_folder / normalized_filename).is_file():
        return url_for("listings.uploaded_file", filename=normalized_filename)

    legacy_upload_folder = Path(current_app.config["LEGACY_UPLOAD_FOLDER"])
    if (legacy_upload_folder / normalized_filename).is_file():
        return url_for("listings.uploaded_file", filename=normalized_filename)

    return url_for("static", filename="images/listing-placeholder.svg")


def strip_upload_prefix(value: str) -> str:
    """Normalize stored upload paths for Python 3.8 compatibility."""

    prefix = "uploads/"
    if value.startswith(prefix):
        return value[len(prefix):]
    return value
