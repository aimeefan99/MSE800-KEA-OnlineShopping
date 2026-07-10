"""Shared badge classes for status labels."""

LISTING_STATUS_BADGE_CLASSES = {
    "available": "status-badge status-badge--available",
    "pending": "status-badge status-badge--pending",
    "sold": "status-badge status-badge--sold",
}
REQUEST_STATUS_BADGE_CLASSES = {
    "pending": "status-badge status-badge--pending",
    "accepted": "status-badge status-badge--completed",
    "completed": "status-badge status-badge--completed",
    "rejected": "status-badge status-badge--sold",
}
DEFAULT_STATUS_BADGE_CLASS = "status-badge status-badge--neutral"


def listing_status_badge_class(status: str) -> str:
    """Return the visual badge class for a listing status."""

    return LISTING_STATUS_BADGE_CLASSES.get(status, DEFAULT_STATUS_BADGE_CLASS)


def request_status_badge_class(status: str) -> str:
    """Return the visual badge class for a request status."""

    return REQUEST_STATUS_BADGE_CLASSES.get(status, DEFAULT_STATUS_BADGE_CLASS)


def lock_status_badge_class(is_locked: bool) -> str:
    """Return the visual badge class for a lock state."""

    if is_locked:
        return "status-badge status-badge--locked"
    return "status-badge status-badge--available"
