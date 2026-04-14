"""Pydantic models for governance API key responses."""

from typing import Optional

from air.types.base import CustomBaseModel


class APIKeyInfo(CustomBaseModel):
    """Metadata about an existing API key (returned by inspect).

    Attributes:
        api_key_id: UUID of the API key.
        user_id: UUID of the user who owns the key.
        organization_id: Organization UUID.
        label: User-defined label.
        permission: Access level (``READ_ONLY`` or ``READ_WRITE``).
        role: RBAC role (``SUPER_ADMIN``, ``ORG_ADMIN``, ``ORG_MEMBER``,
            or ``ORG_VIEWER``).
        expires_date: Expiry date string.
        created_date: Creation date string.
        updated_date: Last update date string.
    """

    api_key_id: str
    user_id: Optional[str] = None
    organization_id: str
    label: Optional[str] = None
    permission: str
    role: str
    expires_date: str
    created_date: str
    updated_date: str


class APIKeyCreated(CustomBaseModel):
    """Response returned when a new API key is created.

    The ``api_key`` field contains the full key and is only available at
    creation time.

    Attributes:
        api_key: The full API key (shown once).
        api_key_id: UUID of the created key.
        organization_id: Organization UUID.
        label: User-defined label.
        permission: Access level.
        role: RBAC role.
        expires_date: Expiry date string.
        created_date: Creation date string.
        updated_date: Last update date string.
    """

    api_key: str
    api_key_id: str
    organization_id: str
    label: str
    permission: str
    role: str
    expires_date: str
    created_date: str
    updated_date: str
