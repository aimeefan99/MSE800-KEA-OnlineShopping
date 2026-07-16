"""Helpers for resolving listing image sources across templates."""

from typing import Any, Dict, List

from services.image_storage_service import image_storage_service


def attach_listing_image_sources(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Attach a resolved image URL to each listing-like dictionary."""

    for listing in listings:
        listing["image_src"] = resolve_listing_image_url(listing.get("image_url"))
    return listings


def resolve_listing_image_url(image_url: str) -> str:
    """Return a browser-safe image URL for the active storage backend."""

    return image_storage_service.resolve_listing_image_url(image_url)


def strip_upload_prefix(value: str) -> str:
    """Normalize stored upload paths for Python 3.8 compatibility."""

    return image_storage_service.normalize_image_reference(value)
