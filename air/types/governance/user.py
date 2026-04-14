"""Pydantic models for governance User responses."""

from datetime import datetime
from typing import Optional

from air.types.base import CustomBaseModel


class User(CustomBaseModel):
    """Represents a user in the governance layer.

    Attributes:
        id: User UUID.
        external_id: External IdP identifier (e.g. Azure AD oid).
        email: User email address.
        display_name: Human-friendly display name.
        status: Current status (``active``, ``inactive``, or ``deleted``).
        created_at: Timestamp when the user was created.
        updated_at: Timestamp of the last update.
        last_login_at: Timestamp of the last login.
        org_id: Organization UUID (included when returned via org-scoped endpoints).
        role: RBAC role in the organization (included when returned via org-scoped endpoints).
    """

    id: str
    external_id: Optional[str] = None
    email: str
    display_name: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    org_id: Optional[str] = None
    role: Optional[str] = None
