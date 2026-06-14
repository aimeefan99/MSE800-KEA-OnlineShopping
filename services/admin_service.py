"""Administrator service placeholders."""


def get_admin_users() -> None:
    """Get users for administrator view."""

    raise NotImplementedError


def get_admin_listings() -> None:
    """Get listings for administrator view."""

    raise NotImplementedError


def get_admin_requests() -> None:
    """Get request records for administrator view."""

    raise NotImplementedError


def delete_inappropriate_listing() -> None:
    """Delete an inappropriate listing."""

    raise NotImplementedError


def get_admin_completed_requests() -> None:
    """Get completed request records for administrator view."""

    raise NotImplementedError


def lock_user_account() -> None:
    """Lock a user account."""

    raise NotImplementedError


def lock_request_record() -> None:
    """Lock a request record."""

    raise NotImplementedError
