"""Pydantic models for governance Workspace responses."""

from datetime import datetime
from typing import Optional

from air.types.base import CustomBaseModel


class Workspace(CustomBaseModel):
    """Represents a workspace within an organization.

    Attributes:
        id: Workspace UUID.
        org_id: Parent organization UUID.
        name: Workspace name (unique within the organization).
        description: Optional workspace description.
        status: Current status (``active``, ``archived``, or ``deleted``).
        created_at: Timestamp when the workspace was created.
        updated_at: Timestamp of the last update.
    """

    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
