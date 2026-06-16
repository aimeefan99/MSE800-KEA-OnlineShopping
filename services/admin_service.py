"""Administrator service placeholders."""

from services.base_service import BaseService


class AdminService(BaseService):
    """Handle administrator control actions."""

    def get_admin_users(self) -> None:
        """Get users for administrator view."""

        raise NotImplementedError

    def get_admin_listings(self) -> None:
        """Get listings for administrator view."""

        raise NotImplementedError

    def get_admin_requests(self) -> None:
        """Get request records for administrator view."""

        raise NotImplementedError

    def delete_inappropriate_listing(self) -> None:
        """Delete an inappropriate listing."""

        raise NotImplementedError

    def get_admin_completed_requests(self) -> None:
        """Get completed request records for administrator view."""

        raise NotImplementedError

    def lock_user_account(self) -> None:
        """Lock a user account."""

        raise NotImplementedError

    def lock_request_record(self) -> None:
        """Lock a request record."""

        raise NotImplementedError


admin_service = AdminService()
