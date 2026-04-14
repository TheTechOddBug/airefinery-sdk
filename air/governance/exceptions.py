"""Exception hierarchy for governance SDK operations."""


class GovernanceError(Exception):
    """Base exception for governance operations.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code from the server (if available).
        response_body: Raw response body dict (if available).
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: dict | None = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class PermissionDeniedError(GovernanceError):
    """Raised on HTTP 403 — caller lacks the required RBAC role."""


class ResourceNotFoundError(GovernanceError):
    """Raised on HTTP 404 — the requested resource does not exist."""


class DuplicateResourceError(GovernanceError):
    """Raised on HTTP 400 when creating a resource that already exists."""


class UnprocessableContentError(GovernanceError):
    """Raised on HTTP 422 when creating a resource with an invalid configuration."""
