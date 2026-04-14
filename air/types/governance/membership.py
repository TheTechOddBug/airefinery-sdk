"""Pydantic models for governance OrgMembership responses."""

from datetime import datetime

from air.types.base import CustomBaseModel


class OrgMembership(CustomBaseModel):
    """Represents a user's membership in an organization.

    Attributes:
        id: Membership UUID.
        org_id: Organization UUID.
        user_id: User UUID.
        role: RBAC role (``SUPER_ADMIN``, ``ORG_ADMIN``, ``ORG_MEMBER``,
            or ``ORG_VIEWER``).
        created_at: Timestamp when the membership was created.
    """

    id: str
    org_id: str
    user_id: str
    role: str
    created_at: datetime
